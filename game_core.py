import math
import random
from datetime import datetime
import json
import os
import sqlite3


class GameCore:
    def __init__(self):
        self.db = None
        self.player_state = None
        self.galaxy_map = []
        self.player_artifacts = []
        self.initialize_database()

    def initialize_database(self):
        try:
            from database import DatabaseManager
            self.db = DatabaseManager()
        except:
            pass

    def load_game_state(self):
        try:
            if not self.db:
                self.initialize_database()

            conn = self.db.get_connection()
            if conn is None:
                return False

            cursor = conn.cursor()

            cursor.execute("SELECT * FROM player_state LIMIT 1")
            player_data = cursor.fetchone()

            if player_data:
                self.player_state = {
                    'id': player_data[0],
                    'name': player_data[1],
                    'race': player_data[2],
                    'level': player_data[3],
                    'exp': player_data[4],
                    'credits': player_data[5],
                    'ship_speed': player_data[6],
                    'ship_scanner': player_data[7],
                    'ship_shields': player_data[8],
                    'ship_energy': player_data[9],
                    'current_system': player_data[10] if player_data[10] else 1,
                    'unlocked_regions': json.loads(player_data[11]) if player_data[11] else ["alpha"],
                    'last_save': player_data[12],
                    'health': player_data[13] if len(player_data) > 13 and player_data[13] else 100,
                    'max_health': player_data[14] if len(player_data) > 14 and player_data[14] else 100,
                    'total_mined': player_data[15] if len(player_data) > 15 else 0,
                    'total_travel_cost': player_data[16] if len(player_data) > 16 else 0,
                    'debt': player_data[17] if len(player_data) > 17 else 0,
                    'reputation': player_data[18] if len(player_data) > 18 else 0
                }
            else:
                self.player_state = None
                conn.close()
                return False

            self.galaxy_map = self.load_galaxy_map(cursor)

            if self.player_state:
                self.player_artifacts = self.load_player_artifacts(cursor)

            conn.close()
            return True

        except Exception as e:
            print(f"Ошибка при загрузке игры: {e}")
            return False

    def load_galaxy_map(self, cursor):
        try:
            cursor.execute("SELECT * FROM galaxy_map ORDER BY id")
            from models import StarSystem
            systems = []
            for row in cursor.fetchall():
                system = StarSystem.from_db(row)
                systems.append(system)
            return systems
        except Exception as e:
            print(f"Ошибка при загрузке карты галактики: {e}")
            return []

    def load_player_artifacts(self, cursor):
        try:
            cursor.execute('''
                SELECT a.* FROM artifacts a
                JOIN player_archive pa ON a.id = pa.artifact_id
                WHERE pa.player_id = ?
            ''', (self.player_state['id'],))

            from models import Artifact
            artifacts = []
            for row in cursor.fetchall():
                artifact = Artifact.from_db(row)
                artifacts.append(artifact)
            return artifacts
        except Exception as e:
            print(f"Ошибка при загрузке артефактов игрока: {e}")
            return []

    def create_player(self, player_name, race):
        try:
            conn = self.db.get_connection()
            if conn is None:
                return False

            cursor = conn.cursor()

            cursor.execute("DELETE FROM player_state WHERE player_name = ?", (player_name,))
            cursor.execute(
                "DELETE FROM player_archive WHERE player_id IN (SELECT id FROM player_state WHERE player_name = ?)",
                (player_name,))

            base_stats = {
                'human': {'credits': 800, 'health': 100, 'speed': 1, 'scanner': 1, 'shields': 1, 'energy': 1},
                'cyborg': {'credits': 750, 'health': 120, 'speed': 1, 'scanner': 2, 'shields': 1, 'energy': 1},
                'alien': {'credits': 850, 'health': 90, 'speed': 2, 'scanner': 1, 'shields': 1, 'energy': 1},
                'android': {'credits': 775, 'health': 110, 'speed': 1, 'scanner': 1, 'shields': 2, 'energy': 1}
            }

            stats = base_stats.get(race, base_stats['human'])

            cursor.execute('''
                INSERT INTO player_state (player_name, player_race, credits, health, max_health, 
                                        ship_speed, ship_scanner, ship_shields, ship_energy, 
                                        current_system_id, last_save)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (
                player_name,
                race,
                stats['credits'],
                stats['health'],
                stats['health'],
                stats['speed'],
                stats['scanner'],
                stats['shields'],
                stats['energy'],
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return self.load_game_state()

        except Exception as e:
            print(f"Ошибка при создании игрока: {e}")
            return False

    def create_new_game(self):
        try:
            db_file = "space_explorer.db"
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                except:
                    try:
                        import time
                        backup_name = f"space_explorer_backup_{int(time.time())}.db"
                        os.rename(db_file, backup_name)
                    except:
                        try:
                            conn = sqlite3.connect(db_file)
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM player_archive")
                            cursor.execute("DELETE FROM artifacts")
                            cursor.execute("DELETE FROM galaxy_map")
                            cursor.execute("DELETE FROM player_state")
                            conn.commit()
                            conn.close()
                        except:
                            return False

            self.initialize_database()

            self.player_state = None
            self.galaxy_map = []
            self.player_artifacts = []

            return True

        except Exception as e:
            print(f"Ошибка при создании новой игры: {e}")
            return False

    def can_travel_to_system(self, target_system_id):
        if not self.player_state:
            return False, "Нет данных игрока"

        target_system = next((s for s in self.galaxy_map if s.id == target_system_id), None)
        current_system = next((s for s in self.galaxy_map if s.id == self.player_state['current_system']), None)

        if not target_system or not current_system:
            return False, "Система не найдена"

        distance = math.sqrt((target_system.x - current_system.x) ** 2 +
                             (target_system.y - current_system.y) ** 2)

        energy_bonus = 1.0
        if self.player_state['race'] == 'alien':
            energy_bonus = 1.2

        max_distance = self.player_state['ship_energy'] * 150 * energy_bonus

        if distance > max_distance:
            return False, f"Недостаточно энергии!"

        return True, ""

    def travel_to_system(self, system_id):
        if not self.player_state:
            return False, "Нет данных игрока"

        can_travel, travel_msg = self.can_travel_to_system(system_id)
        if not can_travel:
            return False, travel_msg

        target_system = next((s for s in self.galaxy_map if s.id == system_id), None)
        current_system = next((s for s in self.galaxy_map if s.id == self.player_state['current_system']), None)

        if target_system and current_system:
            distance = math.sqrt((target_system.x - current_system.x) ** 2 +
                                 (target_system.y - current_system.y) ** 2)

            speed_bonus = 1.0
            if self.player_state['race'] == 'android':
                speed_bonus = 0.9

            base_cost = int(distance / 40 * speed_bonus)
            danger_cost = target_system.danger_level * 4
            difficulty_cost = target_system.difficulty * 3

            multipliers = {
                "poor": 0.9,
                "average": 1.0,
                "rich": 1.2,
                "booming": 1.4,
                "depressed": 0.8
            }
            economy_multiplier = multipliers.get(getattr(target_system, 'economy_status', 'average'), 1.0)

            total_cost = int((base_cost + danger_cost + difficulty_cost) * economy_multiplier)

            if self.player_state['credits'] >= total_cost:
                self.player_state['credits'] -= total_cost
                self.player_state['total_travel_cost'] = self.player_state.get('total_travel_cost', 0) + total_cost
                self.player_state['current_system'] = system_id

                conn = self.db.get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE galaxy_map SET discovered = TRUE WHERE id = ?
                    ''', (system_id,))
                    conn.commit()
                    conn.close()

                target_system.discovered = True

                shield_bonus = 1.0
                if self.player_state['race'] == 'cyborg':
                    shield_bonus = 0.8

                danger_result = self.check_travel_dangers(target_system, shield_bonus)
                if danger_result:
                    success, danger_msg = danger_result
                    if not success:
                        return False, danger_msg
                    else:
                        success_msg = f"Прибыли в {target_system.name}. Потрачено: {total_cost} кредитов"
                        final_msg = success_msg + ". " + danger_msg
                        self.save_game()
                        return True, final_msg

                self.save_game()
                return True, f"Прибыли в {target_system.name}. Потрачено: {total_cost} кредитов"
            else:
                return False, f"Недостаточно кредитов. Нужно: {total_cost}, у вас: {self.player_state['credits']}"

        return False, "Невозможно путешествовать в эту систему"

    def check_travel_dangers(self, target_system, shield_bonus=1.0):
        if not self.player_state:
            return None

        base_danger_chance = target_system.danger_level * 0.25 * shield_bonus

        faction = getattr(target_system, 'faction', None)
        if faction == 'pirate':
            base_danger_chance += 0.3
        elif faction == 'military' and self.player_state.get('reputation', 0) < 0:
            base_danger_chance += 0.2

        if target_system.special_encounter:
            base_danger_chance += 0.15

        if random.random() < base_danger_chance:
            event_type = self.get_random_travel_event(target_system)
            return self.handle_travel_event(event_type, target_system, shield_bonus)

        elif target_system.special_encounter and random.random() < 0.20:
            bonus = random.randint(50, 150) + (self.player_state['level'] * 20)
            self.player_state['credits'] += bonus
            self.save_game()
            return True, f"★ Особое событие! Найдены ресурсы на сумму {bonus} кредитов"

        return None

    def get_random_travel_event(self, system):
        events = [
            "pirate_attack",
            "asteroid_storm",
            "space_whale",
            "trader",
            "abandoned_station",
            "anomaly",
            "quantum_flux",
            "black_market",
            "scientific_expedition"
        ]

        faction = getattr(system, 'faction', None)
        if faction == 'pirate':
            events.extend(['pirate_attack'] * 3)
        elif faction == 'corporate':
            events.extend(['trader'] * 2)
        elif faction == 'scientific':
            events.extend(['scientific_expedition', 'anomaly'])

        return random.choice(events)

    def handle_travel_event(self, event_type, system, shield_bonus):
        if event_type == "pirate_attack":
            damage = system.danger_level * 15
            defense_bonus = 1.0
            if self.player_state['race'] == 'cyborg':
                defense_bonus = 0.8
            shield_protection = self.player_state['ship_shields'] * 5 * defense_bonus
            damage = max(10, int(damage - shield_protection))

            self.player_state['health'] -= damage
            self.player_state['health'] = max(0, self.player_state['health'])

            if self.player_state['health'] <= 0:
                return self.handle_ship_destruction("Пиратская атака уничтожила ваш корабль!")

            loot_loss = random.randint(50, 200)
            self.player_state['credits'] = max(0, self.player_state['credits'] - loot_loss)
            self.save_game()
            return True, f"⚔ Пиратская атака! Урон: {damage}, Потеряно кредитов: {loot_loss}"

        elif event_type == "asteroid_storm":
            damage = system.danger_level * 12
            damage = max(8, damage)

            if random.random() < 0.3:
                speed_reduction = random.randint(1, 3)
                self.player_state['ship_speed'] = max(1, self.player_state['ship_speed'] - speed_reduction)
                self.save_game()
                return True, f"☄ Шторм астероидов! Урон: {damage}, Скорость снижена на {speed_reduction}"
            else:
                self.player_state['health'] -= damage
                self.player_state['health'] = max(0, self.player_state['health'])
                self.save_game()
                return True, f"☄ Шторм астероидов! Урон: {damage}"

        elif event_type == "trader":
            if random.random() < 0.6:
                goods_value = random.randint(100, 400)
                self.player_state['credits'] += goods_value
                self.save_game()
                return True, f"🛒 Встретили торговца! Получено: {goods_value} кредитов"
            else:
                scam_loss = random.randint(50, 200)
                self.player_state['credits'] = max(0, self.player_state['credits'] - scam_loss)
                self.save_game()
                return True, f"🛒 Торговец оказался мошенником! Потеряно: {scam_loss} кредитов"

        elif event_type == "abandoned_station":
            if random.random() < 0.5:
                salvage = random.randint(200, 600)
                self.player_state['credits'] += salvage
                self.save_game()
                return True, f"🏚 На заброшенной станции найдены ресурсы: {salvage} кредитов"
            else:
                trap_damage = random.randint(20, 60)
                self.player_state['health'] -= trap_damage
                self.player_state['health'] = max(0, self.player_state['health'])
                self.save_game()
                return True, f"🏚 Ловушка на станции! Урон: {trap_damage}"

        elif event_type == "black_market":
            artifact_discount = random.randint(10, 40)
            bonus = random.randint(100, 300)
            self.player_state['credits'] += bonus
            self.save_game()
            return True, f"🕶 Чёрный рынок! Скидка на артефакты: {artifact_discount}%, Бонус: +{bonus} кредитов"

        return None

    def handle_ship_destruction(self, reason):
        self.player_state['health'] = self.player_state['max_health'] // 3
        penalty = 150
        self.player_state['credits'] = max(0, self.player_state['credits'] - penalty)
        self.player_state['current_system'] = 1

        if self.player_state['credits'] < 50:
            debt = 50 - self.player_state['credits']
            self.player_state['debt'] = self.player_state.get('debt', 0) + debt
            self.player_state['credits'] = 0

        conn = self.db.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE galaxy_map SET discovered = TRUE WHERE id = 1
            ''')
            conn.commit()
            conn.close()

        start_system = self.get_system_by_id(1)
        if start_system:
            start_system.discovered = True

        self.save_game()
        return False, f"{reason} Потеряно {penalty} кредитов. Возвращены на старт."

    def mine_artifact(self, system_id):
        if not self.player_state:
            return False, "Нет данных игрока"

        system = next((s for s in self.galaxy_map if s.id == system_id), None)
        if not system or not system.has_artifact or system.id != self.player_state['current_system']:
            return False, "В этой системе нет артефактов"

        if self.player_state['health'] < 50:
            return False, f"Слишком мало здоровья ({self.player_state['health']}%) для добычи. Минимум 50%"

        conn = self.db.get_connection()
        if conn is None:
            return False, "Ошибка подключения к базе данных"

        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM artifacts 
            WHERE system_id = ? AND is_available = TRUE
            ORDER BY rarity DESC, value DESC
            LIMIT 1
        ''', (system_id,))
        artifact_data = cursor.fetchone()

        if not artifact_data:
            conn.close()
            return False, "Все артефакты в этой системе уже добыты"

        from models import Artifact
        artifact = Artifact.from_db(artifact_data)

        base_mining_cost = system.base_mining_cost + artifact.mining_cost
        difficulty_cost = system.difficulty * 6
        danger_cost = system.danger_level * 4

        multipliers = {
            "poor": 0.9,
            "average": 1.0,
            "rich": 1.2,
            "booming": 1.4,
            "depressed": 0.8
        }
        economy_multiplier = multipliers.get(getattr(system, 'economy_status', 'average'), 1.0)

        total_mining_cost = int((base_mining_cost + difficulty_cost + danger_cost) * economy_multiplier)

        if self.player_state['credits'] < total_mining_cost:
            conn.close()
            return False, f"Недостаточно кредитов для добычи. Нужно: {total_mining_cost}"

        mining_danger = self.check_mining_dangers(system, total_mining_cost)
        if mining_danger:
            success, danger_msg = mining_danger
            if not success:
                conn.close()
                return False, danger_msg

        scanner_bonus = 1.0
        if self.player_state['race'] == 'cyborg':
            scanner_bonus = 1.2

        base_success = 0.40 + (self.player_state['ship_scanner'] * 0.12 * scanner_bonus)
        if system.difficulty > 3:
            base_success -= (system.difficulty - 3) * 0.08

        success_chance = min(0.75, base_success)

        if random.random() < success_chance:
            self.player_state['credits'] -= total_mining_cost
            self.player_state['total_mined'] = self.player_state.get('total_mined', 0) + total_mining_cost

            cursor.execute('''
                INSERT INTO player_archive (artifact_id, player_id, acquisition_date)
                VALUES (?, ?, ?)
            ''', (artifact.id, self.player_state['id'], datetime.now().isoformat()))

            cursor.execute('''
                UPDATE artifacts SET is_available = FALSE 
                WHERE id = ?
            ''', (artifact.id,))

            cursor.execute('''
                UPDATE galaxy_map 
                SET has_artifact = FALSE, artifact_type = NULL,
                    last_artifact_respawn = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), system_id))

            reward_bonus = 1.0
            if self.player_state['race'] == 'human':
                reward_bonus = 1.12

            reward_multiplier = (1.8 + (self.player_state['level'] * 0.15)) * reward_bonus
            reward = int(artifact.value * reward_multiplier)

            exp_reward = artifact.power_level * 120 + system.difficulty * 60
            self.player_state['credits'] += reward
            self.player_state['exp'] += exp_reward

            faction = getattr(system, 'faction', None)
            if faction == 'corporate':
                self.player_state['reputation'] = self.player_state.get('reputation', 0) + 5

            conn.commit()

            system.has_artifact = False
            system.artifact_type = None
            system.last_artifact_respawn = datetime.now().isoformat()

            artifact.equipped = False
            artifact.discovery_date = datetime.now().isoformat()

            if not self.player_artifacts:
                self.player_artifacts = []
            self.player_artifacts.append(artifact)

            conn.close()

            level_up = self.check_level_up()
            self.save_game()

            net_profit = reward - total_mining_cost
            profit_text = f"(Прибыль: {net_profit} кредитов)" if net_profit > 0 else f"(Убыток: {abs(net_profit)} кредитов)"

            if level_up:
                return True, f"Найден {artifact.rarity} артефакт: {artifact.name}! Стоимость добычи: {total_mining_cost}, Награда: +{reward} кредитов, +{exp_reward} опыта. {profit_text}. Уровень повышен!"
            else:
                return True, f"Найден {artifact.rarity} артефакт: {artifact.name}! Стоимость добычи: {total_mining_cost}, Награда: +{reward} кредитов, +{exp_reward} опыта. {profit_text}"
        else:
            self.player_state['credits'] -= total_mining_cost // 2
            self.player_state['total_mined'] = self.player_state.get('total_mined', 0) + (total_mining_cost // 2)
            conn.close()
            self.save_game()
            return False, f"Артефакт не найден. Потрачено: {total_mining_cost // 2} кредитов. Шанс успеха: {success_chance * 100:.1f}%"

    def check_mining_dangers(self, system, mining_cost):
        if not self.player_state:
            return None

        danger_chance = system.danger_level * 0.25

        faction = getattr(system, 'faction', None)
        if faction == 'pirate':
            danger_chance += 0.15

        if danger_chance < 0.20:
            danger_chance = 0.20

        if random.random() < danger_chance:
            event_type = random.choice(["cave_in", "gas_leak", "equipment_failure", "predator_attack"])

            if event_type == "cave_in":
                damage = system.difficulty * 20
                self.player_state['health'] -= damage
                self.player_state['health'] = max(0, self.player_state['health'])

                if self.player_state['health'] <= 0:
                    return self.handle_ship_destruction("Обвал во время добычи уничтожил корабль!")

                lost_tools = random.randint(50, 150)
                self.player_state['credits'] = max(0, self.player_state['credits'] - lost_tools)
                self.save_game()
                return True, f"⚠ Обвал! Урон: {damage}, Потеряно инструментов: {lost_tools} кредитов"

            elif event_type == "gas_leak":
                poison_damage = system.danger_level * 15
                self.player_state['health'] -= poison_damage
                self.player_state['health'] = max(0, self.player_state['health'])

                medical_cost = poison_damage * 3
                if self.player_state['credits'] >= medical_cost:
                    self.player_state['credits'] -= medical_cost
                    self.save_game()
                    return True, f"⚠ Утечка газа! Урон: {poison_damage}, Медицинские расходы: {medical_cost} кредитов"
                else:
                    self.save_game()
                    return True, f"⚠ Утечка газа! Урон: {poison_damage}. Нет средств на лечение"

            elif event_type == "equipment_failure":
                repair_cost = mining_cost // 2
                self.player_state['credits'] = max(0, self.player_state['credits'] - repair_cost)
                self.save_game()
                return True, f"⚠ Поломка оборудования! Ремонт: {repair_cost} кредитов"

            elif event_type == "predator_attack":
                damage = random.randint(30, 80)
                self.player_state['health'] -= damage
                self.player_state['health'] = max(0, self.player_state['health'])

                if random.random() < 0.4:
                    self.save_game()
                    return True, f"⚠ Атака местной фауны! Урон: {damage}. Часть оборудования потеряна"
                else:
                    self.save_game()
                    return True, f"⚠ Атака местной фауны! Урон: {damage}"

        elif system.special_encounter and random.random() < 0.25:
            event_type = random.choice(["rich_vein", "ancient_city", "energy_source"])

            if event_type == "rich_vein":
                bonus = random.randint(150, 450) + (self.player_state['level'] * 40)
                self.player_state['credits'] += bonus
                self.save_game()
                return True, f"★ Богатая жила! Дополнительная добыча: +{bonus} кредитов"

            elif event_type == "ancient_city":
                artifact_bonus = random.randint(200, 600)
                self.player_state['credits'] += artifact_bonus
                self.save_game()
                return True, f"★ Древний город! Найдены артефакты: +{artifact_bonus} кредитов"

            elif event_type == "energy_source":
                self.player_state['ship_energy'] = min(18, self.player_state['ship_energy'] + 1)
                self.save_game()
                return True, f"★ Источник энергии! Уровень энергии увеличен!"

        return None

    def check_level_up(self):
        if not self.player_state:
            return False

        exp_needed = self.player_state['level'] * 1000
        if self.player_state['exp'] >= exp_needed:
            self.player_state['level'] += 1
            self.player_state['exp'] -= exp_needed
            self.player_state['credits'] += self.player_state['level'] * 250
            self.player_state['max_health'] += 15
            self.player_state['health'] = self.player_state['max_health']
            self.save_game()
            return True
        return False

    def upgrade_ship(self, upgrade_type):
        if not self.player_state:
            return False, "Нет данных игрока"

        cost_multiplier = 1.0
        if self.player_state['race'] == 'human':
            cost_multiplier = 0.85

        upgrade_base_costs = {
            'speed': 200,
            'scanner': 250,
            'shields': 220,
            'energy': 180
        }

        current_level = self.player_state[f'ship_{upgrade_type}']
        cost = int(upgrade_base_costs[upgrade_type] * current_level * cost_multiplier)

        max_level = 15

        if current_level >= max_level:
            return False, f"Максимальный уровень ({max_level}) достигнут"

        if self.player_state['credits'] >= cost:
            self.player_state['credits'] -= cost
            self.player_state[f'ship_{upgrade_type}'] += 1

            if upgrade_type == 'shields':
                self.player_state['max_health'] += 15
                self.player_state['health'] = min(self.player_state['max_health'], self.player_state['health'] + 12)

            self.save_game()
            return True, f"{upgrade_type.capitalize()} улучшено до уровня {self.player_state[f'ship_{upgrade_type}']}. Стоимость: {cost} кредитов"
        else:
            return False, f"Недостаточно кредитов. Нужно: {cost}"

    def repair_ship(self):
        if not self.player_state:
            return False, "Нет данных игрока"

        if self.player_state['health'] >= self.player_state['max_health']:
            return False, "Корабль уже полностью отремонтирован"

        repair_cost_per_hp = 8
        repair_cost = (self.player_state['max_health'] - self.player_state['health']) * repair_cost_per_hp

        if self.player_state['credits'] >= repair_cost:
            self.player_state['credits'] -= repair_cost
            self.player_state['health'] = self.player_state['max_health']
            self.save_game()
            return True, f"Корабль отремонтирован за {repair_cost} кредитов"
        else:
            max_repair = self.player_state['credits'] // repair_cost_per_hp
            if max_repair > 0:
                repair_amount = min(max_repair, self.player_state['max_health'] - self.player_state['health'])
                partial_cost = repair_amount * repair_cost_per_hp
                self.player_state['credits'] -= partial_cost
                self.player_state['health'] += repair_amount
                self.save_game()
                return True, f"Частичный ремонт: +{repair_amount} здоровья за {partial_cost} кредитов"
            else:
                return False, f"Недостаточно кредитов для ремонта. Нужно минимум {repair_cost_per_hp} кредитов"

    def pay_debt(self):
        if not self.player_state:
            return False, "Нет данных игрока"

        debt = self.player_state.get('debt', 0)
        if debt <= 0:
            return False, "У вас нет долгов"

        interest = int(debt * 0.1)
        total_due = debt + interest

        if self.player_state['credits'] >= total_due:
            self.player_state['credits'] -= total_due
            self.player_state['debt'] = 0
            self.save_game()
            return True, f"Долг погашен: {debt} + {interest} (проценты) = {total_due} кредитов"
        else:
            return False, f"Недостаточно кредитов для погашения долга. Нужно: {total_due}"

    def get_system_by_id(self, system_id):
        return next((s for s in self.galaxy_map if s.id == system_id), None)

    def save_game(self):
        try:
            if not self.player_state:
                return False

            conn = self.db.get_connection()
            if conn is None:
                return False

            cursor = conn.cursor()

            cursor.execute('''
                UPDATE player_state 
                SET level = ?, experience = ?, credits = ?, ship_speed = ?,
                    ship_scanner = ?, ship_shields = ?, ship_energy = ?,
                    current_system_id = ?, unlocked_regions = ?, last_save = ?,
                    health = ?, max_health = ?, total_mined = ?, total_travel_cost = ?,
                    debt = ?, reputation = ?
                WHERE id = ?
            ''', (
                self.player_state['level'],
                self.player_state['exp'],
                self.player_state['credits'],
                self.player_state['ship_speed'],
                self.player_state['ship_scanner'],
                self.player_state['ship_shields'],
                self.player_state['ship_energy'],
                self.player_state['current_system'],
                json.dumps(self.player_state['unlocked_regions']),
                datetime.now().isoformat(),
                self.player_state['health'],
                self.player_state['max_health'],
                self.player_state['total_mined'],
                self.player_state['total_travel_cost'],
                self.player_state.get('debt', 0),
                self.player_state.get('reputation', 0),
                self.player_state['id']
            ))

            for system in self.galaxy_map:
                cursor.execute('''
                    UPDATE galaxy_map 
                    SET discovered = ?, has_artifact = ?, artifact_type = ?,
                        last_artifact_respawn = ?
                    WHERE id = ?
                ''', (
                    system.discovered,
                    system.has_artifact,
                    system.artifact_type,
                    system.last_artifact_respawn,
                    system.id
                ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Ошибка при сохранении игры: {e}")
            return False

    def show_message(self, message):
        pass