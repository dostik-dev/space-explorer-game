from enum import Enum
import json


class ArtifactType(Enum):
    TECH = "TECH"
    LORE = "LORE"
    ARTIFACT = "ARTIFACT"
    KEY = "KEY"
    RELIC = "RELIC"
    BIOLOGICAL = "BIOLOGICAL"


class Artifact:
    def __init__(self, id, name, type, rarity, description, value, power_level, system_id,
                 discovery_date=None, image_path=None, is_available=True, bonus_effect=None, mining_cost=0):
        self.id = id
        self.name = name
        self.type = ArtifactType(type) if isinstance(type, str) else type
        self.rarity = rarity
        self.description = description
        self.value = value
        self.power_level = power_level
        self.system_id = system_id
        self.discovery_date = discovery_date
        self.image_path = image_path
        self.is_available = is_available
        self.bonus_effect = bonus_effect
        self.mining_cost = mining_cost
        self.equipped = False

    @classmethod
    def from_db(cls, db_row):
        row_list = list(db_row)
        while len(row_list) < 13:
            row_list.append(None)

        return cls(
            row_list[0],
            row_list[1],
            row_list[2],
            row_list[3],
            row_list[4],
            row_list[5],
            row_list[6],
            row_list[7],
            row_list[8] if len(row_list) > 8 else None,
            row_list[9] if len(row_list) > 9 else None,
            row_list[10] if len(row_list) > 10 else True,
            row_list[11] if len(row_list) > 11 else None,
            row_list[12] if len(row_list) > 12 else 0
        )


class StarSystem:
    def __init__(self, id, name, x, y, region, discovered, has_artifact,
                 artifact_type, difficulty, connections, last_artifact_respawn=None,
                 respawn_timer=120, danger_level=1, special_encounter=False,
                 base_mining_cost=30, economy_status="average", population=0,
                 faction=None):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.region = region
        self.discovered = discovered
        self.has_artifact = has_artifact
        self.artifact_type = artifact_type
        self.difficulty = difficulty
        self.connections = json.loads(connections) if isinstance(connections, str) else connections
        self.last_artifact_respawn = last_artifact_respawn
        self.respawn_timer = respawn_timer
        self.danger_level = danger_level
        self.special_encounter = special_encounter
        self.base_mining_cost = base_mining_cost
        self.economy_status = economy_status
        self.population = population
        self.faction = faction
        self.click_radius = 40

    @classmethod
    def from_db(cls, db_row):
        row_list = list(db_row)
        while len(row_list) < 19:
            row_list.append(None)

        return cls(
            row_list[0],
            row_list[1],
            row_list[2],
            row_list[3],
            row_list[4],
            bool(row_list[5]),
            bool(row_list[6]),
            row_list[7],
            row_list[8] if row_list[8] is not None else 1,
            row_list[9] if row_list[9] is not None else '[]',
            row_list[10],
            row_list[11] if row_list[11] is not None else 120,
            row_list[12] if row_list[12] is not None else 1,
            bool(row_list[13]) if row_list[13] is not None else False,
            row_list[14] if row_list[14] is not None else 30,
            row_list[15] if row_list[15] is not None else "average",
            row_list[16] if row_list[16] is not None else 0,
            row_list[17]
        )
