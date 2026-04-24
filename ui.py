import arcade
import math
import random


class SpaceExplorerGame(arcade.Window):
    def __init__(self):
        super().__init__(1400, 900, "Космический Исследователь", resizable=True)
        arcade.set_background_color(arcade.color.BLACK)

        self.game_core = None
        self.initialize_game_core()

        self.current_screen = "main_menu"
        self.selected_system = None
        self.message = ""
        self.message_timer = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.camera_scale = 1.0
        self.min_scale = 0.3
        self.max_scale = 3.0
        self.player_name = "Исследователь"
        self.selected_race = None

        self.races = {
            'human': {
                'name': 'Человек',
                'color': arcade.color.SKY_BLUE,
                'bonuses': [
                    '+8% к доходу от артефактов',
                    '-15% стоимость улучшений',
                    'Баланс во всем'
                ],
                'description': 'Экономист'
            },
            'cyborg': {
                'name': 'Киборг',
                'color': arcade.color.ELECTRIC_GREEN,
                'bonuses': [
                    '+20% к шансу добычи',
                    '+20% защита от опасностей',
                    '+20 здоровья'
                ],
                'description': 'Технолог'
            },
            'alien': {
                'name': 'Инопланетянин',
                'color': arcade.color.PURPLE,
                'bonuses': [
                    '+20% дальность полета',
                    'Старт: скорость +1',
                    '-12% стоимость путешествий'
                ],
                'description': 'Путешественник'
            },
            'android': {
                'name': 'Андроид',
                'color': arcade.color.ORANGE,
                'bonuses': [
                    '+25% защита щитов',
                    '+15 здоровья',
                    '-10% стоимость ремонта'
                ],
                'description': 'Защитник'
            }
        }

        self.artifact_colors = {
            "TECH": arcade.color.CYBER_YELLOW,
            "LORE": arcade.color.LIGHT_BLUE,
            "ARTIFACT": arcade.color.EMERALD,
            "KEY": arcade.color.MAGENTA,
            "RELIC": arcade.color.GOLD,
            "BIOLOGICAL": arcade.color.GREEN
        }

        self.faction_colors = {
            "pirate": arcade.color.RED,
            "corporate": arcade.color.BLUE,
            "neutral": arcade.color.GRAY,
            "military": arcade.color.DARK_GREEN,
            "scientific": arcade.color.CYAN,
            "mining": arcade.color.ORANGE
        }

        self.economy_colors = {
            "poor": arcade.color.RED,
            "average": arcade.color.YELLOW,
            "rich": arcade.color.GREEN,
            "booming": arcade.color.CYAN,
            "depressed": arcade.color.DARK_RED
        }

        self.active_buttons = {
            'travel_button': None,
            'mine_button': None,
            'repair_button': None,
            'debt_button': None
        }

        self.init_ui()

    def initialize_game_core(self):
        try:
            from game_core import GameCore
            self.game_core = GameCore()
            self.game_core.show_message = self.show_message
        except Exception as e:
            print(f"Ошибка инициализации GameCore: {e}")
            self.game_core = None

    def init_ui(self):
        self.ui_elements = {
            'resource_panel': {
                'x': 10, 'y': self.height - 40,
                'width': 800, 'height': 40
            },
            'system_info': {
                'x': self.width - 450, 'y': self.height - 280,
                'width': 440, 'height': 270
            },
            'camera_info': {
                'x': self.width - 150, 'y': 30,
                'width': 140, 'height': 60
            },
            'menu_buttons': [
                ("Новая игра", self.width // 2, self.height // 2 + 100, 400, 60, self.new_game),
                ("Продолжить", self.width // 2, self.height // 2 + 30, 400, 60, self.continue_game),
                ("Архив артефактов", self.width // 2, self.height // 2 - 40, 400, 60, self.show_archive),
                ("Улучшения корабля", self.width // 2, self.height // 2 - 110, 400, 60, self.show_upgrades),
                ("Выход", self.width // 2, self.height // 2 - 180, 400, 60, self.exit_game)
            ],
            'title': {
                'text': "КОСМИЧЕСКИЙ ИССЛЕДОВАТЕЛЬ",
                'x': self.width // 2,
                'y': self.height - 100,
                'size': 48,
                'color': arcade.color.GOLD
            }
        }

    def on_draw(self):
        self.clear()
        self.draw_background()

        if self.current_screen == "main_menu":
            self.draw_main_menu()
        elif self.current_screen == "race_selection":
            self.draw_race_selection()
        elif self.current_screen == "name_input":
            self.draw_name_input()
        elif self.current_screen == "galaxy_map":
            self.draw_galaxy_map()
        elif self.current_screen == "archive":
            self.draw_archive()
        elif self.current_screen == "upgrades":
            self.draw_upgrades()

        if self.current_screen not in ["main_menu", "race_selection", "name_input"]:
            self.draw_resource_panel()

        if self.message:
            self.draw_message()

        if self.current_screen not in ["main_menu", "race_selection", "name_input"]:
            self.draw_navigation()

        if self.current_screen == "galaxy_map":
            self.draw_camera_info()

    def draw_background(self):
        for i in range(150):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            size = random.randrange(1, 4)
            brightness = random.randrange(150, 255)
            arcade.draw_circle_filled(x, y, size, (brightness, brightness, brightness))

        for i in range(3):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            size = random.randrange(20, 50)
            arcade.draw_circle_filled(x, y, size, (50, 50, 100, 100))

    def draw_main_menu(self):
        title = self.ui_elements['title']
        arcade.draw_text(title['text'], title['x'], title['y'],
                         title['color'], title['size'],
                         align="center", anchor_x="center", anchor_y="center")

        for text, x, y, width, height, action in self.ui_elements['menu_buttons']:
            left = x - width // 2
            right = x + width // 2
            bottom = y - height // 2
            top = y + height // 2

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.GRAY, 3)
            arcade.draw_text(text, x, y, arcade.color.WHITE, 24,
                             align="center", anchor_x="center", anchor_y="center")

    def draw_race_selection(self):
        arcade.draw_text("ВЫБОР РАСЫ", self.width // 2, self.height - 80,
                         arcade.color.GOLD, 48, align="center", anchor_x="center")

        arcade.draw_text("Выберите вашу расу:", self.width // 2, self.height - 140,
                         arcade.color.WHITE, 24, align="center", anchor_x="center")

        race_positions = [
            (self.width // 4, self.height // 2 + 120, 'human'),
            (self.width * 3 // 4, self.height // 2 + 120, 'cyborg'),
            (self.width // 4, self.height // 2 - 120, 'alien'),
            (self.width * 3 // 4, self.height // 2 - 120, 'android')
        ]

        for x, y, race_id in race_positions:
            race = self.races[race_id]

            left = x - 160
            right = x + 160
            bottom = y - 90
            top = y + 90

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (40, 40, 60, 200))
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, race['color'], 3)

            arcade.draw_text(race['name'], x, y + 60, race['color'], 24,
                             align="center", anchor_x="center", bold=True)

            arcade.draw_text(race['description'], x, y + 35, arcade.color.LIGHT_GRAY, 14,
                             align="center", anchor_x="center")

            arcade.draw_text("Бонусы:", x - 150, y + 10, arcade.color.WHITE, 16, bold=True)
            for i, bonus in enumerate(race['bonuses']):
                arcade.draw_text(f"• {bonus}", x - 140, y - i * 18, arcade.color.LIGHT_GRAY, 12, width=280)

            btn_left = x - 70
            btn_right = x + 70
            btn_bottom = y - 75
            btn_top = y - 50

            arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, race['color'])
            arcade.draw_text("ВЫБРАТЬ", x, btn_bottom + 12, arcade.color.WHITE, 16,
                             align="center", anchor_x="center")

    def draw_name_input(self):
        arcade.draw_text("СОЗДАНИЕ ИГРОКА", self.width // 2, self.height - 100,
                         arcade.color.GOLD, 36, align="center", anchor_x="center")

        arcade.draw_text("Введите имя вашего исследователя:", self.width // 2, self.height - 180,
                         arcade.color.WHITE, 24, align="center", anchor_x="center")

        input_left = self.width // 2 - 200
        input_right = self.width // 2 + 200
        input_bottom = self.height // 2
        input_top = input_bottom + 50

        arcade.draw_lrbt_rectangle_filled(input_left, input_right, input_bottom, input_top, (60, 60, 80))
        arcade.draw_lrbt_rectangle_outline(input_left, input_right, input_bottom, input_top, arcade.color.WHITE, 2)

        arcade.draw_text(self.player_name, self.width // 2, input_bottom + 15,
                         arcade.color.WHITE, 28, align="center", anchor_x="center")

        btn_left = self.width // 2 - 150
        btn_right = btn_left + 300
        btn_bottom = input_bottom - 100
        btn_top = btn_bottom + 50

        arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, arcade.color.DARK_GREEN)
        arcade.draw_text("НАЧАТЬ ИГРУ", self.width // 2, btn_bottom + 15,
                         arcade.color.WHITE, 24, align="center", anchor_x="center")

        arcade.draw_text("Нажмите Enter для подтверждения", self.width // 2, btn_bottom - 40,
                         arcade.color.GRAY, 16, align="center", anchor_x="center")

    def draw_galaxy_map(self):
        if not self.game_core or not self.game_core.player_state:
            arcade.draw_text("Нет данных игры", self.width // 2, self.height // 2,
                             arcade.color.RED, 32, align="center", anchor_x="center")
            return

        scale = min(self.width / 1600, self.height / 1200) * 0.8 * self.camera_scale
        center_x = self.width // 2 + self.camera_offset_x
        center_y = self.height // 2 + self.camera_offset_y

        for system in self.game_core.galaxy_map:
            for connection_id in system.connections:
                target_system = next((s for s in self.game_core.galaxy_map if s.id == connection_id), None)
                if target_system:
                    can_travel, _ = self.game_core.can_travel_to_system(connection_id)
                    if can_travel or (system.discovered and target_system.discovered):
                        color = arcade.color.GRAY
                    else:
                        color = arcade.color.DARK_GRAY

                    arcade.draw_line(
                        system.x * scale + center_x,
                        system.y * scale + center_y,
                        target_system.x * scale + center_x,
                        target_system.y * scale + center_y,
                        color, 2
                    )

        for system in self.game_core.galaxy_map:
            x = system.x * scale + center_x
            y = system.y * scale + center_y

            if system.id == self.game_core.player_state['current_system']:
                color = arcade.color.GOLD
                size = 35
            elif system.discovered:
                if system.faction and system.faction in self.faction_colors:
                    color = self.faction_colors[system.faction]
                else:
                    color = arcade.color.SKY_BLUE
                size = 28
            else:
                color = arcade.color.DARK_GRAY
                size = 22

            arcade.draw_circle_filled(x, y, size, color)
            arcade.draw_circle_outline(x, y, size, arcade.color.WHITE, 2)

            if system.discovered:
                arcade.draw_text(system.name, x - 60, y - 40,
                                 arcade.color.WHITE, 10, align="center", width=120)

            if system.has_artifact:
                artifact_color = self.artifact_colors.get(system.artifact_type, arcade.color.WHITE)
                arcade.draw_circle_filled(x, y + 40, 10, artifact_color)
                arcade.draw_circle_outline(x, y + 40, 10, arcade.color.WHITE, 1)

                if system.special_encounter:
                    points = []
                    for i in range(12):
                        angle = math.pi * 2 * i / 12
                        if i % 2 == 0:
                            radius = 8
                        else:
                            radius = 4
                        points.append((x + math.cos(angle) * radius, y - 40 + math.sin(angle) * radius))

                    if len(points) >= 3:
                        arcade.draw_polygon_filled(points, arcade.color.YELLOW)

        if self.selected_system:
            self.draw_system_info(self.selected_system)

    def draw_resource_panel(self):
        if not self.game_core or not self.game_core.player_state:
            return

        panel = self.ui_elements['resource_panel']
        left = panel['x']
        right = left + panel['width']
        bottom = panel['y'] - panel['height']
        top = panel['y']

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (30, 30, 50, 200))

        info = self.game_core.player_state
        race_info = self.races[info['race']]

        health_percent = (info['health'] / info['max_health']) * 100
        health_color = arcade.color.GREEN
        if health_percent < 60:
            health_color = arcade.color.ORANGE
        if health_percent < 30:
            health_color = arcade.color.RED

        health_bar_width = 120
        health_fill = int(health_bar_width * (health_percent / 100))

        arcade.draw_lrbt_rectangle_filled(panel['x'] + 10, panel['x'] + 10 + health_fill,
                                          panel['y'] - 15, panel['y'] - 5, health_color)
        arcade.draw_lrbt_rectangle_outline(panel['x'] + 10, panel['x'] + 10 + health_bar_width,
                                           panel['y'] - 15, panel['y'] - 5, arcade.color.WHITE, 1)

        race_color = race_info['color']

        debt_text = ""
        if info.get('debt', 0) > 0:
            debt_text = f" | Долг: {info['debt']}"

        reputation_text = ""
        rep = info.get('reputation', 0)
        if rep != 0:
            reputation_text = f" | Репутация: {rep}"

        text = f"{info['name']} ({race_info['name']}) | Ур: {info['level']} | "
        text += f"Опыт: {info['exp']}/{info['level'] * 1200} | "
        text += f"Кредиты: {info['credits']} | Здоровье: {info['health']}/{info['max_health']}{debt_text}{reputation_text}"

        arcade.draw_text(text, panel['x'] + 140, panel['y'] - 25,
                         arcade.color.WHITE, 11)

    def draw_system_info(self, system):
        if not self.game_core or not self.game_core.player_state:
            return

        info_panel = self.ui_elements['system_info']
        left = info_panel['x']
        right = left + info_panel['width']
        bottom = info_panel['y'] - info_panel['height']
        top = info_panel['y']

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (20, 20, 40, 230))

        y_offset = info_panel['y'] - 30
        arcade.draw_text(system.name, info_panel['x'] + 20, y_offset,
                         arcade.color.WHITE, 22, bold=True)
        y_offset -= 35

        if system.discovered:
            region_color = arcade.color.SKY_BLUE
            arcade.draw_text(f"Регион: {system.region}", info_panel['x'] + 20, y_offset,
                             region_color, 18)
            y_offset -= 25

            if system.faction:
                faction_color = self.faction_colors.get(system.faction, arcade.color.WHITE)
                arcade.draw_text(f"Фракция: {system.faction}", info_panel['x'] + 20, y_offset,
                                 faction_color, 16)
                y_offset -= 25

            if system.economy_status:
                economy_color = self.economy_colors.get(system.economy_status, arcade.color.WHITE)
                arcade.draw_text(f"Экономика: {system.economy_status}", info_panel['x'] + 20, y_offset,
                                 economy_color, 16)
                y_offset -= 25

            danger_color = arcade.color.GREEN
            if system.danger_level >= 4:
                danger_color = arcade.color.RED
            elif system.danger_level >= 2:
                danger_color = arcade.color.YELLOW

            arcade.draw_text(f"Опасность: {system.danger_level}/5", info_panel['x'] + 20, y_offset,
                             danger_color, 18)
            y_offset -= 30

            if system.special_encounter:
                arcade.draw_text("★ Особое событие", info_panel['x'] + 20, y_offset,
                                 arcade.color.YELLOW, 16, bold=True)
                y_offset -= 25

            if system.has_artifact:
                artifact_color = self.artifact_colors.get(system.artifact_type, arcade.color.WHITE)
                arcade.draw_text(f"Артефакт: {system.artifact_type}", info_panel['x'] + 20, y_offset,
                                 artifact_color, 18)
                y_offset -= 25
                arcade.draw_text(f"Базовая стоимость добычи: {system.base_mining_cost}",
                                 info_panel['x'] + 20, y_offset,
                                 arcade.color.LIGHT_GRAY, 14)
                y_offset -= 20
            else:
                arcade.draw_text("Артефакт: Нет", info_panel['x'] + 20, y_offset,
                                 arcade.color.GRAY, 18)
                y_offset -= 30

            self.active_buttons['travel_button'] = None
            self.active_buttons['mine_button'] = None

            if system.id != self.game_core.player_state['current_system']:
                btn_left = info_panel['x'] + 20
                btn_right = btn_left + 200
                btn_bottom = y_offset - 20
                btn_top = btn_bottom + 40

                can_travel, travel_msg = self.game_core.can_travel_to_system(system.id)

                if can_travel:
                    btn_color = arcade.color.DARK_GREEN
                else:
                    btn_color = arcade.color.DARK_RED

                self.active_buttons['travel_button'] = (btn_left, btn_right, btn_bottom, btn_top, system.id)

                arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, btn_color)
                arcade.draw_text("ПУТЕШЕСТВИЕ", btn_left + 50, btn_bottom + 10,
                                 arcade.color.WHITE, 16)

                if not can_travel:
                    arcade.draw_text(travel_msg[:25], btn_left + 50, btn_bottom - 5,
                                     arcade.color.RED, 10, align="center", width=180)

            if system.has_artifact and system.id == self.game_core.player_state['current_system']:
                btn_left = info_panel['x'] + 230
                btn_right = btn_left + 190
                btn_bottom = y_offset - 20
                btn_top = btn_bottom + 40

                self.active_buttons['mine_button'] = (btn_left, btn_right, btn_bottom, btn_top, system.id)

                arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, arcade.color.DARK_BLUE)
                arcade.draw_text("ДОБЫТЬ", btn_left + 60, btn_bottom + 10,
                                 arcade.color.WHITE, 16)
        else:
            arcade.draw_text("НЕ ИССЛЕДОВАНО", info_panel['x'] + 20, y_offset,
                             arcade.color.GRAY, 18)
            y_offset -= 30

            btn_left = info_panel['x'] + 20
            btn_right = btn_left + 200
            btn_bottom = y_offset - 20
            btn_top = btn_bottom + 40

            can_travel, travel_msg = self.game_core.can_travel_to_system(system.id)

            if can_travel:
                btn_color = arcade.color.DARK_GREEN
            else:
                btn_color = arcade.color.DARK_RED

            self.active_buttons['travel_button'] = (btn_left, btn_right, btn_bottom, btn_top, system.id)

            arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, btn_color)
            arcade.draw_text("ИССЛЕДОВАТЬ", btn_left + 40, btn_bottom + 10,
                             arcade.color.WHITE, 16)

            if not can_travel:
                arcade.draw_text(travel_msg[:25], btn_left + 50, btn_bottom - 5,
                                 arcade.color.RED, 10, align="center", width=180)

    def draw_archive(self):
        if not self.game_core or not self.game_core.player_state:
            arcade.draw_text("Нет данных игры", self.width // 2, self.height // 2,
                             arcade.color.RED, 32, align="center", anchor_x="center")
            return

        arcade.draw_text("АРХИВ АРТЕФАКТОВ", self.width // 2, self.height - 80,
                         arcade.color.GOLD, 32, align="center", anchor_x="center")

        artifacts = self.game_core.player_artifacts
        if not artifacts:
            arcade.draw_text("Артефакты не найдены", self.width // 2, self.height // 2,
                             arcade.color.GRAY, 24, align="center", anchor_x="center")
            return

        artifacts_by_type = {}
        for artifact in artifacts:
            artifact_type = artifact.type.value if hasattr(artifact.type, 'value') else artifact.type
            if artifact_type not in artifacts_by_type:
                artifacts_by_type[artifact_type] = []
            artifacts_by_type[artifact_type].append(artifact)

        y_start = self.height - 140
        x_start = 100
        x_offset = 0
        y_offset = 0
        max_per_column = 8

        for artifact_type, type_artifacts in artifacts_by_type.items():
            if x_offset >= 2:
                x_offset = 0
                y_offset += 1

            type_color = self.artifact_colors.get(artifact_type, arcade.color.WHITE)
            arcade.draw_text(f"{artifact_type} ({len(type_artifacts)})",
                             x_start + x_offset * 500, y_start - y_offset * 400,
                             type_color, 22, bold=True)

            for i, artifact in enumerate(type_artifacts[:max_per_column]):
                y_pos = y_start - 50 - y_offset * 400 - i * 45
                arcade.draw_text(f"{artifact.name}",
                                 x_start + x_offset * 500 + 30, y_pos,
                                 arcade.color.LIGHT_GRAY, 16)
                arcade.draw_text(f"{artifact.rarity} - {artifact.value} cr",
                                 x_start + x_offset * 500 + 30, y_pos - 20,
                                 arcade.color.GRAY, 14)
                if artifact.mining_cost > 0:
                    arcade.draw_text(f"Стоимость добычи: {artifact.mining_cost}",
                                     x_start + x_offset * 500 + 30, y_pos - 35,
                                     arcade.color.DARK_GRAY, 12)

            if len(type_artifacts) > max_per_column:
                arcade.draw_text(f"... и ещё {len(type_artifacts) - max_per_column}",
                                 x_start + x_offset * 500 + 30,
                                 y_start - 50 - y_offset * 400 - max_per_column * 45,
                                 arcade.color.DARK_GRAY, 14)

            x_offset += 1

        total_value = sum(a.value for a in artifacts)
        total_mining_cost = sum(a.mining_cost for a in artifacts)
        total_profit = total_value - total_mining_cost
        epic_count = sum(1 for a in artifacts if a.rarity == "EPIC")
        legendary_count = sum(1 for a in artifacts if a.rarity == "LEGENDARY")
        key_count = sum(1 for a in artifacts if hasattr(a.type, 'value') and a.type.value == "KEY" or a.type == "KEY")

        stats_text = f"Всего артефактов: {len(artifacts)} | Общая стоимость: {total_value:,} cr | "
        stats_text += f"Общие затраты на добычу: {total_mining_cost:,} cr | "
        stats_text += f"Общая прибыль: {total_profit:,} cr"
        if epic_count > 0:
            stats_text += f" | EPIC: {epic_count}"
        if legendary_count > 0:
            stats_text += f" | LEGENDARY: {legendary_count}"
        if key_count > 0:
            stats_text += f" | Ключи: {key_count}"

        arcade.draw_text(stats_text, self.width // 2, 50,
                         arcade.color.WHITE, 16, align="center", anchor_x="center")

    def draw_upgrades(self):
        if not self.game_core or not self.game_core.player_state:
            arcade.draw_text("Нет данных игры", self.width // 2, self.height // 2,
                             arcade.color.RED, 32, align="center", anchor_x="center")
            return

        arcade.draw_text("УЛУЧШЕНИЯ КОРАБЛЯ", self.width // 2, self.height - 80,
                         arcade.color.CYAN, 32, align="center", anchor_x="center")

        upgrades = [
            ("Энергия", self.game_core.player_state['ship_energy'],
             "Увеличивает дальность полета", "energy"),
            ("Щиты", self.game_core.player_state['ship_shields'],
             "Защита от опасностей, +15 здоровья за уровень", "shields"),
            ("Сканер", self.game_core.player_state['ship_scanner'],
             "Увеличивает шанс найти артефакт (+12% за уровень)", "scanner"),
            ("Скорость", self.game_core.player_state['ship_speed'],
             "Уменьшает стоимость путешествий", "speed")
        ]

        y_start = self.height - 160
        for i, (name, level, description, upgrade_type) in enumerate(upgrades):
            y_pos = y_start - i * 120
            left = self.width // 2 - 300
            right = self.width // 2 + 300
            bottom = y_pos - 50
            top = y_pos + 50

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (40, 40, 60, 200))

            arcade.draw_text(name, self.width // 2 - 250, y_pos + 20,
                             arcade.color.WHITE, 22, bold=True)
            arcade.draw_text(f"Уровень: {level}/15", self.width // 2 - 250, y_pos - 10,
                             arcade.color.LIGHT_GRAY, 18)
            arcade.draw_text(description, self.width // 2 - 250, y_pos - 35,
                             arcade.color.GRAY, 16, width=500)

            upgrade_cost = 0
            if upgrade_type == "speed":
                upgrade_cost = level * 250
            elif upgrade_type == "scanner":
                upgrade_cost = level * 300
            elif upgrade_type == "shields":
                upgrade_cost = level * 280
            elif upgrade_type == "energy":
                upgrade_cost = level * 220

            max_level = 15
            can_upgrade = level < max_level
            can_afford = self.game_core.player_state['credits'] >= upgrade_cost

            if can_upgrade and can_afford:
                btn_color = arcade.color.DARK_GREEN
            else:
                btn_color = arcade.color.DARK_RED

            btn_left = self.width // 2 + 150
            btn_right = btn_left + 120
            btn_bottom = y_pos - 25
            btn_top = btn_bottom + 25

            arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, btn_color)
            arcade.draw_text(f"{upgrade_cost}", self.width // 2 + 210, y_pos - 5,
                             arcade.color.WHITE, 18, align="center", anchor_x="center")
            arcade.draw_text("УЛУЧШИТЬ", self.width // 2 + 210, y_pos - 25,
                             arcade.color.WHITE, 12, align="center", anchor_x="center")

        repair_y = self.height - 640
        arcade.draw_text("РЕМОНТ И ФИНАНСЫ", self.width // 2, repair_y - 20,
                         arcade.color.ORANGE, 22, align="center", anchor_x="center")

        if self.game_core.player_state['health'] < self.game_core.player_state['max_health']:
            repair_cost = (self.game_core.player_state['max_health'] - self.game_core.player_state['health']) * 12
            can_repair = self.game_core.player_state['credits'] >= repair_cost

            btn_left = self.width // 2 - 230
            btn_right = btn_left + 200
            btn_bottom = repair_y - 70
            btn_top = btn_bottom + 40

            repair_color = arcade.color.DARK_GREEN if can_repair else arcade.color.DARK_RED
            arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, repair_color)
            arcade.draw_text(f"РЕМОНТ ({repair_cost})", self.width // 2 - 130, btn_bottom + 10,
                             arcade.color.WHITE, 16, align="center", anchor_x="center")

            self.active_buttons['repair_button'] = (btn_left, btn_right, btn_bottom, btn_top)

        debt = self.game_core.player_state.get('debt', 0)
        if debt > 0:
            total_due = int(debt * 1.1)
            btn_left = self.width // 2 + 30
            btn_right = btn_left + 200
            btn_bottom = repair_y - 70
            btn_top = btn_bottom + 40

            can_pay = self.game_core.player_state['credits'] >= total_due
            debt_color = arcade.color.DARK_GREEN if can_pay else arcade.color.DARK_RED

            arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bottom, btn_top, debt_color)
            arcade.draw_text(f"ПОГАСИТЬ ДОЛГ", self.width // 2 + 130, btn_bottom + 10,
                             arcade.color.WHITE, 16, align="center", anchor_x="center")
            arcade.draw_text(f"{total_due} кредитов", self.width // 2 + 130, btn_bottom - 5,
                             arcade.color.YELLOW, 12, align="center", anchor_x="center")

            self.active_buttons['debt_button'] = (btn_left, btn_right, btn_bottom, btn_top)

    def draw_camera_info(self):
        info_panel = self.ui_elements['camera_info']
        left = info_panel['x']
        right = left + info_panel['width']
        bottom = info_panel['y'] - info_panel['height']
        top = info_panel['y']

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (30, 30, 50, 200))

        arcade.draw_text("КАРТА", left + 45, top - 20, arcade.color.WHITE, 16, bold=True)
        arcade.draw_text(f"Масштаб: {self.camera_scale:.1f}x", left + 10, top - 45,
                         arcade.color.LIGHT_GRAY, 14)
        arcade.draw_text("ПКМ - тащить", left + 20, bottom + 10, arcade.color.GRAY, 10)

    def draw_message(self):
        if self.message_timer > 0:
            alpha = min(255, self.message_timer * 5)
            left = self.width // 2 - 400
            right = self.width // 2 + 400
            bottom = 100
            top = 160

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, int(alpha * 0.7)))
            arcade.draw_text(self.message, self.width // 2, 130,
                             (255, 255, 255, int(alpha)), 20,
                             align="center", anchor_x="center", anchor_y="center")
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""

    def draw_navigation(self):
        buttons = [
            ("КАРТА", 100, 60, self.show_galaxy_map),
            ("АРХИВ", 250, 60, self.show_archive),
            ("УЛУЧШЕНИЯ", 400, 60, self.show_upgrades),
            ("СОХРАНИТЬ", 550, 60, self.save_game_func),
            ("МЕНЮ", 700, 60, self.show_main_menu),
            ("ВЫХОД", 850, 60, self.exit_game)
        ]
        for text, x, y, action in buttons:
            width = 140
            left = x - width // 2
            right = x + width // 2
            bottom = y - 20
            top = y + 20

            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
            arcade.draw_text(text, x, y - 8, arcade.color.WHITE, 14,
                             align="center", anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_screen == "main_menu":
            for text, btn_x, btn_y, width, height, action in self.ui_elements['menu_buttons']:
                left = btn_x - width // 2
                right = btn_x + width // 2
                bottom = btn_y - height // 2
                top = btn_y + height // 2

                if left <= x <= right and bottom <= y <= top:
                    action()
                    return

        elif self.current_screen == "race_selection":
            race_positions = [
                (self.width // 4, self.height // 2 + 120, 'human'),
                (self.width * 3 // 4, self.height // 2 + 120, 'cyborg'),
                (self.width // 4, self.height // 2 - 120, 'alien'),
                (self.width * 3 // 4, self.height // 2 - 120, 'android')
            ]

            for race_x, race_y, race_id in race_positions:
                btn_left = race_x - 70
                btn_right = race_x + 70
                btn_bottom = race_y - 75
                btn_top = race_y - 50

                if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                    self.selected_race = race_id
                    self.current_screen = "name_input"
                    return

        elif self.current_screen == "name_input":
            btn_left = self.width // 2 - 150
            btn_right = btn_left + 300
            btn_bottom = self.height // 2 - 100
            btn_top = btn_bottom + 50

            if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                self.start_game_with_player()
                return

        else:
            nav_buttons = [
                (30, 170, 40, 80, self.show_galaxy_map),
                (180, 320, 40, 80, self.show_archive),
                (330, 470, 40, 80, self.show_upgrades),
                (480, 620, 40, 80, self.save_game_func),
                (630, 770, 40, 80, self.show_main_menu),
                (780, 920, 40, 80, self.exit_game)
            ]

            for x1, x2, y1, y2, action in nav_buttons:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    action()
                    return

        if self.current_screen == "galaxy_map":
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.handle_galaxy_map_click(x, y)
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.is_dragging = True
                self.drag_start_x = x - self.camera_offset_x
                self.drag_start_y = y - self.camera_offset_y

        elif self.current_screen == "upgrades":
            self.handle_upgrades_click(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT and self.current_screen == "galaxy_map":
            self.is_dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.is_dragging and buttons == arcade.MOUSE_BUTTON_RIGHT:
            self.camera_offset_x = x - self.drag_start_x
            self.camera_offset_y = y - self.drag_start_y

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.current_screen == "galaxy_map":
            scale_change = 0.1
            if scroll_y > 0:
                self.camera_scale = min(self.max_scale, self.camera_scale + scale_change)
            elif scroll_y < 0:
                self.camera_scale = max(self.min_scale, self.camera_scale - scale_change)

    def new_game(self):
        if not self.game_core:
            self.initialize_game_core()

        success = self.game_core.create_new_game()
        if success:
            self.current_screen = "race_selection"
            self.selected_race = None
            self.player_name = "Исследователь"
            self.show_message("Новая игра создана! Выберите расу.")
        else:
            self.show_message("Ошибка создания новой игры. Перезапустите игру.")

    def continue_game(self):
        if not self.game_core:
            self.initialize_game_core()

        success = self.game_core.load_game_state()
        if success and self.game_core.player_state:
            self.show_message("Сохранение загружено!")
            self.current_screen = "galaxy_map"
        else:
            self.show_message("Сохранение не найдено. Начните новую игру.")

    def show_archive(self):
        if self.game_core and self.game_core.player_state:
            self.current_screen = "archive"
        else:
            self.show_message("Нет данных игры")

    def show_upgrades(self):
        if self.game_core and self.game_core.player_state:
            self.current_screen = "upgrades"
        else:
            self.show_message("Нет данных игры")

    def exit_game(self):
        if self.game_core and self.game_core.player_state:
            self.save_game_func()
        self.close()

    def show_galaxy_map(self):
        if self.game_core and self.game_core.player_state:
            self.current_screen = "galaxy_map"
        else:
            self.show_message("Нет данных игры")

    def show_main_menu(self):
        self.current_screen = "main_menu"
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_scale = 1.0

    def handle_galaxy_map_click(self, x, y):
        if not self.game_core or not self.game_core.player_state:
            self.show_message("Нет данных игры")
            return

        scale = min(self.width / 1600, self.height / 1200) * 0.8 * self.camera_scale
        center_x = self.width // 2 + self.camera_offset_x
        center_y = self.height // 2 + self.camera_offset_y

        if self.active_buttons['mine_button']:
            btn_left, btn_right, btn_bottom, btn_top, system_id = self.active_buttons['mine_button']
            if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                success, msg = self.game_core.mine_artifact(system_id)
                self.show_message(msg)
                self.selected_system = None
                self.active_buttons['mine_button'] = None
                return

        if self.active_buttons['travel_button']:
            btn_left, btn_right, btn_bottom, btn_top, system_id = self.active_buttons['travel_button']
            if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                success, msg = self.game_core.travel_to_system(system_id)
                self.show_message(msg)
                self.selected_system = None
                self.active_buttons['travel_button'] = None
                return

        for system in self.game_core.galaxy_map:
            sys_x = system.x * scale + center_x
            sys_y = system.y * scale + center_y

            distance = math.sqrt((x - sys_x) ** 2 + (y - sys_y) ** 2)
            radius = system.click_radius * (1.0 / self.camera_scale)

            if distance <= radius:
                self.selected_system = system
                return

        self.selected_system = None
        self.active_buttons['travel_button'] = None
        self.active_buttons['mine_button'] = None

    def handle_upgrades_click(self, x, y):
        if not self.game_core or not self.game_core.player_state:
            self.show_message("Нет данных игры")
            return

        upgrades_mapping = {0: "energy", 1: "shields", 2: "scanner", 3: "speed"}
        y_start = self.height - 160

        for i in range(4):
            y_pos = y_start - i * 120
            if (self.width // 2 + 150 <= x <= self.width // 2 + 270 and
                    y_pos - 25 <= y <= y_pos + 25):
                upgrade_type = upgrades_mapping[i]
                success, msg = self.game_core.upgrade_ship(upgrade_type)
                self.show_message(msg)
                return

        if self.active_buttons.get('repair_button'):
            btn_left, btn_right, btn_bottom, btn_top = self.active_buttons['repair_button']
            if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                success, msg = self.game_core.repair_ship()
                self.show_message(msg)
                self.active_buttons['repair_button'] = None
                return

        if self.active_buttons.get('debt_button'):
            btn_left, btn_right, btn_bottom, btn_top = self.active_buttons['debt_button']
            if btn_left <= x <= btn_right and btn_bottom <= y <= btn_top:
                success, msg = self.game_core.pay_debt()
                self.show_message(msg)
                self.active_buttons['debt_button'] = None
                return

    def show_message(self, message):
        self.message = message
        self.message_timer = 100

    def save_game_func(self):
        if not self.game_core or not self.game_core.player_state:
            self.show_message("Нет данных игры для сохранения")
            return

        success = self.game_core.save_game()
        if success:
            self.show_message("Игра сохранена успешно!")
        else:
            self.show_message("Ошибка сохранения игры!")

    def start_game_with_player(self):
        if hasattr(self, 'selected_race') and self.selected_race:
            if not self.game_core:
                self.initialize_game_core()

            success = self.game_core.create_player(self.player_name, self.selected_race)
            if success:
                self.current_screen = "galaxy_map"
                self.show_message(f"Добро пожаловать, {self.player_name} ({self.races[self.selected_race]['name']})!")
            else:
                self.show_message("Ошибка создания персонажа!")
        else:
            self.show_message("Сначала выберите расу!")

    def update(self, delta_time):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.game_core and self.game_core.player_state:
                self.save_game_func()
            self.close()

        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

        if key == arcade.key.F5:
            self.save_game_func()
            self.show_message("Быстрое сохранение!")

        if key == arcade.key.R:
            self.camera_offset_x = 0
            self.camera_offset_y = 0
            self.camera_scale = 1.0
            self.show_message("Камера сброшена")

        if key == arcade.key.BACKSPACE:
            if self.current_screen == "name_input" and len(self.player_name) > 0:
                self.player_name = self.player_name[:-1]

        elif key == arcade.key.ENTER or key == arcade.key.RETURN:
            if self.current_screen == "name_input":
                self.start_game_with_player()

    def on_text(self, text):
        if self.current_screen == "name_input":
            if text.isprintable() and len(self.player_name) < 20:
                self.player_name += text

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.init_ui()
