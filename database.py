import sqlite3
import json
import random
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_name="space_explorer.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    def close_connection(self, conn):
        if conn:
            conn.close()

    def init_database(self):
        conn = self.get_connection()
        if conn is None:
            print("Не удалось подключиться к базе данных")
            return

        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_state (
                id INTEGER PRIMARY KEY,
                player_name TEXT,
                player_race TEXT DEFAULT 'human',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                credits INTEGER DEFAULT 800,
                ship_speed INTEGER DEFAULT 1,
                ship_scanner INTEGER DEFAULT 1,
                ship_shields INTEGER DEFAULT 1,
                ship_energy INTEGER DEFAULT 1,
                current_system_id INTEGER DEFAULT 1,
                unlocked_regions TEXT DEFAULT '["alpha"]',
                last_save TIMESTAMP,
                health INTEGER DEFAULT 100,
                max_health INTEGER DEFAULT 100,
                total_mined INTEGER DEFAULT 0,
                total_travel_cost INTEGER DEFAULT 0,
                debt INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS galaxy_map (
                id INTEGER PRIMARY KEY,
                name TEXT,
                x REAL,
                y REAL,
                region TEXT,
                discovered BOOLEAN DEFAULT FALSE,
                has_artifact BOOLEAN DEFAULT FALSE,
                artifact_type TEXT,
                difficulty INTEGER DEFAULT 1,
                connections TEXT DEFAULT '[]',
                last_artifact_respawn TIMESTAMP,
                respawn_timer INTEGER DEFAULT 120,
                danger_level INTEGER DEFAULT 1,
                special_encounter BOOLEAN DEFAULT FALSE,
                base_mining_cost INTEGER DEFAULT 20,
                economy_status TEXT DEFAULT 'average',
                population INTEGER DEFAULT 0,
                faction TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                rarity TEXT,
                description TEXT,
                value INTEGER,
                power_level INTEGER DEFAULT 1,
                system_id INTEGER,
                discovery_date TIMESTAMP,
                image_path TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                bonus_effect TEXT,
                mining_cost INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_archive (
                id INTEGER PRIMARY KEY,
                artifact_id INTEGER,
                player_id INTEGER,
                equipped BOOLEAN DEFAULT FALSE,
                acquisition_date TIMESTAMP,
                FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
            )
        ''')

        cursor.execute("SELECT COUNT(*) FROM player_state")
        if cursor.fetchone()[0] == 0:
            self.initialize_game_data(cursor)

        conn.commit()
        conn.close()

    def create_branching_galaxy(self):
        systems = []

        systems.append({
            'name': "Solara Prime",
            'x': 600,
            'y': 450,
            'region': "alpha",
            'connections': [2, 3, 4],
            'has_artifact': True,
            'artifact_type': "TECH",
            'difficulty': 1,
            'danger_level': 1,
            'special_encounter': True,
            'base_mining_cost': 20,
            'economy_status': 'average',
            'population': 5000,
            'faction': 'neutral'
        })

        close_systems = [
            ("Nebula-X1", 750, 550, [1, 5], "alpha", "LORE", 1, 1, 25, True, 'poor', 2000, 'pirate'),
            ("Quantum Drift", 450, 550, [1, 6], "alpha", "TECH", 1, 1, 28, False, 'rich', 10000, 'corporate'),
            ("Stellar Forge", 650, 350, [1, 7], "alpha", "ARTIFACT", 2, 2, 32, True, 'booming', 15000, 'mining')
        ]

        for i, (name, x, y, connections, region, artifact_type, difficulty, danger, mining_cost, special, economy, pop,
                faction) in enumerate(close_systems, 2):
            systems.append({
                'name': name,
                'x': x,
                'y': y,
                'region': region,
                'connections': connections,
                'has_artifact': True,
                'artifact_type': artifact_type,
                'difficulty': difficulty,
                'danger_level': danger,
                'special_encounter': special,
                'base_mining_cost': mining_cost,
                'economy_status': economy,
                'population': pop,
                'faction': faction
            })

        medium_systems = [
            ("Void's Edge", 900, 650, [2, 8], "alpha", "KEY", 2, 2, 38, True, 'depressed', 500, 'pirate'),
            ("Orion Cluster", 350, 700, [3, 9], "alpha", "TECH", 2, 2, 42, False, 'average', 8000, 'neutral'),
            ("Celestial Spire", 800, 250, [4, 10], "alpha", "RELIC", 2, 2, 45, True, 'rich', 12000, 'scientific')
        ]

        for i, (name, x, y, connections, region, artifact_type, difficulty, danger, mining_cost, special, economy, pop,
                faction) in enumerate(medium_systems, 5):
            systems.append({
                'name': name,
                'x': x,
                'y': y,
                'region': region,
                'connections': connections,
                'has_artifact': True,
                'artifact_type': artifact_type,
                'difficulty': difficulty,
                'danger_level': danger,
                'special_encounter': special,
                'base_mining_cost': mining_cost,
                'economy_status': economy,
                'population': pop,
                'faction': faction
            })

        far_systems = [
            ("Black Hole Nexus", 1100, 750, [5, 11], "beta", "ARTIFACT", 3, 3, 50, True, 'poor', 1000, 'pirate'),
            ("Supernova Remnant", 250, 850, [6, 12], "beta", "KEY", 3, 3, 55, False, 'average', 6000, 'military'),
            ("Cosmic Web Hub", 1050, 150, [7, 13], "beta", "BIOLOGICAL", 3, 3, 60, True, 'rich', 20000, 'scientific')
        ]

        for i, (name, x, y, connections, region, artifact_type, difficulty, danger, mining_cost, special, economy, pop,
                faction) in enumerate(far_systems, 8):
            systems.append({
                'name': name,
                'x': x,
                'y': y,
                'region': region,
                'connections': connections,
                'has_artifact': True,
                'artifact_type': artifact_type,
                'difficulty': difficulty,
                'danger_level': danger,
                'special_encounter': special,
                'base_mining_cost': mining_cost,
                'economy_status': economy,
                'population': pop,
                'faction': faction
            })

        extreme_systems = [
            ("Quantum Rift-1", 1300, 450, [11, 14], "gamma", "RELIC", 4, 4, 70, True, 'booming', 30000, 'corporate'),
            ("Ancient Gateway", 1500, 650, [11, 15], "gamma", "KEY", 4, 4, 75, False, 'depressed', 800, 'pirate'),
            ("Dimension Rift", 1200, 850, [12, 16], "gamma", "TECH", 4, 4, 80, True, 'average', 10000, 'neutral')
        ]

        for i, (name, x, y, connections, region, artifact_type, difficulty, danger, mining_cost, special, economy, pop,
                faction) in enumerate(extreme_systems, 11):
            systems.append({
                'name': name,
                'x': x,
                'y': y,
                'region': region,
                'connections': connections,
                'has_artifact': True,
                'artifact_type': artifact_type,
                'difficulty': difficulty,
                'danger_level': danger,
                'special_encounter': special,
                'base_mining_cost': mining_cost,
                'economy_status': economy,
                'population': pop,
                'faction': faction
            })

        return systems

    def initialize_game_data(self, cursor):
        galaxy_systems = self.create_branching_galaxy()

        for i, system in enumerate(galaxy_systems, 1):
            cursor.execute('''
                INSERT INTO galaxy_map (id, name, x, y, region, discovered, has_artifact, 
                                      artifact_type, difficulty, connections, last_artifact_respawn, 
                                      respawn_timer, danger_level, special_encounter, base_mining_cost,
                                      economy_status, population, faction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                i,
                system['name'],
                system['x'],
                system['y'],
                system['region'],
                i <= 3,
                system['has_artifact'],
                system['artifact_type'],
                system['difficulty'],
                json.dumps(system['connections']),
                datetime.now().isoformat(),
                180,
                system['danger_level'],
                system['special_encounter'],
                system['base_mining_cost'],
                system['economy_status'],
                system['population'],
                system['faction']
            ))

        artifact_names = {
            "TECH": ["Quantum Processor", "Energy Core", "Warp Drive", "Shield Generator", "AI Matrix"],
            "LORE": ["Ancient Tablet", "Alien Codex", "Prophecy Scroll", "Celestial Map", "History Stone"],
            "ARTIFACT": ["Crystal Shard", "Void Fragment", "Quantum Essence", "Ethereal Crystal", "Stardust"],
            "KEY": ["Portal Fragment", "Dimensional Key", "Access Crystal", "Pathfinder Stone", "Gateway Seal"],
            "RELIC": ["Elder Relic", "Firstborn Artifact", "Creator's Tool", "Genesis Fragment"],
            "BIOLOGICAL": ["Xeno DNA Sample", "Living Crystal", "Organic Processor", "Neural Network"]
        }

        bonus_effects = [
            "+5% скорость", "+6% сканирование", "+8% защита", "+7% энергия",
            "+10% доход", "-8% стоимость улучшений", "+15 здоровья"
        ]

        artifact_id = 1
        for system_id in range(1, len(galaxy_systems) + 1):
            system = galaxy_systems[system_id - 1]
            artifact_type = system['artifact_type']
            if artifact_type:
                for _ in range(random.randint(1, 2)):
                    rarity_weights = {
                        "COMMON": 60,
                        "RARE": 25,
                        "EPIC": 10,
                        "LEGENDARY": 5
                    }
                    rarity = random.choices(
                        list(rarity_weights.keys()),
                        weights=list(rarity_weights.values())
                    )[0]

                    value_rarity = {"COMMON": 250, "RARE": 500, "EPIC": 900, "LEGENDARY": 1500}
                    power_rarity = {"COMMON": 1, "RARE": 2, "EPIC": 4, "LEGENDARY": 7}
                    mining_cost_rarity = {"COMMON": 15, "RARE": 30, "EPIC": 60, "LEGENDARY": 100}

                    value = value_rarity[rarity] + random.randint(-30, 50)
                    power = power_rarity[rarity] + random.randint(0, 1)
                    mining_cost = mining_cost_rarity[rarity] + random.randint(0, 25)

                    cursor.execute('''
                        INSERT INTO artifacts (id, name, type, rarity, description, value,
                                              power_level, system_id, is_available, bonus_effect, mining_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        artifact_id,
                        random.choice(artifact_names[artifact_type]),
                        artifact_type,
                        rarity,
                        f"{rarity.lower()} {artifact_type.lower()} found in {system['name']}",
                        value,
                        power,
                        system_id,
                        True,
                        random.choice(bonus_effects) if rarity in ["EPIC", "LEGENDARY"] else None,
                        mining_cost
                    ))
                    artifact_id += 1

    def create_player(self, player_name, race):
        try:
            conn = self.get_connection()
            if conn is None:
                return False

            cursor = conn.cursor()

            cursor.execute("SELECT id FROM player_state WHERE player_name = ?", (player_name,))
            existing_player = cursor.fetchone()

            if existing_player:
                player_id = existing_player[0]
                cursor.execute("DELETE FROM player_archive WHERE player_id = ?", (player_id,))
                cursor.execute("DELETE FROM player_state WHERE id = ?", (player_id,))

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

            return True

        except Exception as e:
            print(f"Ошибка при создании игрока: {e}")
            return False