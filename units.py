from enum import Enum
from typing import List

class UnitType(Enum):
    infantry = 1
    vehicle = 2
    aircraft = 3
    naval = 4
    aa = 5
    artilery = 6
    fortification = 7

class Unit:
    attack_roll: int = None
    defense_roll: int = None
    first_strike = False
    cost: int = None
    researched: bool = True
    movement: int = None
    unit_type: UnitType = None
    carpet_bombing: bool = False
    first_strike: bool = False
    attack_count: int = 1
    initial_attack_only: bool = False
    target_select: dict = {}
    already_attacked: bool = False # used for those units with `initial_attack_only = True`, shows that an attack has already happened 
    artillery_paired: bool = False # temp value to show that the unit is already paired with an artillery
    simulation: bool = False # temp value to show that the unit should not make permenant changes to its state

    def get_attack(self, friendlies: List["Unit"]) -> int:
        """
        Gets the attack for this given turn when including friendly unit synergy

        **WARNING** This mutates the `Unit` object and one must run `reset_synergy` after
        """
        return self.attack_roll

    def get_defense(self, friendlies: List["Unit"]) -> int:
        """
        Gets the defense for this given turn when including friendly unit synergy

        **WARNING** This mutates the `Unit` object and one must run `reset_synergy` after
        """
        return self.defense_roll

    def reset_synergy(self):
        """
        To be ran after running `get_attack` or `get_defense`
        """
        self.artillery_paired = False

    def can_attack(self) -> bool:
        if self.initial_attack_only:
            if self.already_attacked:
                return False
            if not self.simulation:
                self.already_attacked = True
            return True
        return True


def valid_target_vehicle(target: Unit) -> bool:
    """
    To be used by target select to see if it is a valid target
    """
    return target.unit_type == UnitType.vehicle

def valid_target_ground_or_naval_unit(target: Unit) -> bool:
    """
    To be used by target select to see if it is a valid target
    """
    return target.unit_type in [
        UnitType.aa,
        UnitType.artilery,
        UnitType.infantry,
        UnitType.vehicle,
        UnitType.naval,
    ]


class InfantryUnit(Unit):
    def get_attack(self, friendlies: List["Unit"]) -> int:
        for friend in friendlies:
            if friend == self:
                continue
            if friend.unit_type == UnitType.artilery and not friend.artillery_paired:
                self.artillery_paired = True
                friend.artillery_paired = True
                return self.attack_roll + 1
        return self.attack_roll

    def get_defense(self, friendlies: List["Unit"]) -> int:
        for friend in friendlies:
            if friend == self:
                continue
            if friend.unit_type == UnitType.artilery and not friend.artillery_paired:
                self.artillery_paired = True
                friend.artillery_paired = True
                return self.defense_roll + 1
        return self.defense_roll

class Militia(InfantryUnit):
    attack_roll = 1
    defense_roll = 2
    cost = 2
    movement = 1
    unit_type = UnitType.infantry

class Infantry(InfantryUnit):
    attack_roll = 2
    defense_roll = 4
    cost = 3
    movement = 1

class AirborneInfantry(InfantryUnit):
    attack_roll = 2
    defense_roll = 2
    cost = 3
    movement = 1
    unit_type = UnitType.infantry
    # Get plus one on initial airdrop

class EliteAirborneInfantry(InfantryUnit):
    attack_roll = 3
    defense_roll = 3
    cost = 3
    movement = 1
    researched = False
    unit_type = UnitType.infantry
    # Get plus one on initial airdrop

class Marines(InfantryUnit):
    attack_roll = 2
    defense_roll = 4
    movement = 1
    cost = 4
    unit_type = UnitType.infantry

class MountainInfantry(InfantryUnit):
    attack_roll = 2
    defense_roll = 4
    movement = 1
    cost = 4
    unit_type = UnitType.infantry

class Cavalry(Unit):
    attack_roll = 3
    defense_roll = 2
    movement = 2
    cost = 3
    unit_type = UnitType.vehicle

class MotorizedInfantry(Unit):
    attack_roll = 2
    defense_roll = 4
    movement = 2
    cost = 4
    unit_type = UnitType.vehicle

class MechanizedInfantry(Unit):
    attack_roll = 3
    defense_roll = 4
    movement = 2
    cost = 4
    researched = False
    unit_type = UnitType.vehicle

class AdvancedMechanizedInfantry(Unit):
    attack_roll = 4
    defense_roll = 5
    movement = 2
    cost = 4
    researched = False
    unit_type = UnitType.vehicle

class TankDestroyer(Unit):
    attack_roll = 3
    defense_roll = 4
    movement = 2
    cost = 5
    unit_type = UnitType.vehicle
    target_select = {
        "roll": 3,
        "valid_targets": valid_target_vehicle,
    }

class LightArmor(Unit):
    attack_roll = 3
    defense_roll = 1
    movement = 2
    cost = 4
    unit_type = UnitType.vehicle

class MediumArmor(Unit):
    attack_roll = 6
    defense_roll = 5
    movement = 2
    cost = 6
    researched = False
    unit_type = UnitType.vehicle

class T34(Unit):
    attack_roll = 6
    defense_roll = 5
    movement = 2
    cost = 5
    researched = False
    unit_type = UnitType.vehicle
    target_select = {
        "roll": 1,
        "valid_targets": valid_target_vehicle,
    }

class HeavyArmor(Unit):
    attack_roll = 8
    defense_roll = 5
    movement = 2
    cost = 7
    researched = False
    unit_type = UnitType.vehicle
    target_select = {
        "roll": 1,
        "valid_targets": valid_target_vehicle,
    }

class Artillery(Unit):
    attack_roll = 3
    defense_roll = 3
    movement = 1
    cost = 4
    unit_type = UnitType.artilery
    first_strike = True
    # does not take attacking penalities across rivers, takes all others as normal (FOR ALL ARTILLERY TYPES)

class SPA(Unit):
    attack_roll = 3
    defense_roll = 3
    movement = 2
    cost = 5
    unit_type = UnitType.vehicle
    first_strike = True

class AdvancedArtillery(Unit):
    attack_roll = 4
    defense_roll = 4
    movement = 1
    cost = 4
    researched = False
    unit_type = UnitType.vehicle
    first_strike = True

class AdvancedSPA(Unit):
    attack_roll = 4
    defense_roll = 4
    movement = 2
    cost = 5
    researched = False
    unit_type = UnitType.artilery
    first_strike = True

class Katyusha(Unit):
    attack_roll = 5
    defense_roll = 4
    movement = 2
    cost = 5
    researched = False
    unit_type = UnitType.vehicle
    first_strike = True

class AAArtillery(Unit):
    attack_roll = 3
    defense_roll = 3
    movement = 1
    cost = 4
    unit_type = UnitType.aa
    # Can only attack on first round
    # Each AA gets one shot at a plane up to 3 planes
    # It only targets planes
    # If no planes in combat, AAA does not do anything

class Fighter(Unit):
    attack_roll = 6
    defense_roll = 6
    movement = 4
    cost = 10
    unit_type = UnitType.aircraft
    # On the first round, fighers target other aircraft, the loser picks which one, not picking seaplanes

class JetFighter(Unit):
    attack_roll = 8
    defense_roll = 8
    movement = 4
    cost = 12
    researched = False
    unit_type = UnitType.aircraft
    # On the first round, fighers target other aircraft, the loser picks which one, not picking seaplanes

class TacticalBomber(Unit):
    attack_roll = 7
    defense_roll = 5
    movement = 4
    cost = 11
    unit_type = UnitType.aircraft
    target_select = {
        "roll": 3,
        "valid_targets": valid_target_ground_or_naval_unit,
    }

class MediumBomber(Unit):
    attack_roll = 7
    defense_roll = 4
    movement = 5
    cost = 11
    unit_type = UnitType.aircraft

class StrategicBomber(Unit):
    attack_roll = 3
    defense_roll = 2
    movement = 6
    cost = 12
    researched = False
    unit_type = UnitType.aircraft
    carpet_bombing = True

class HeavyStrategicBomber(Unit):
    attack_roll = 5
    defense_roll = 3
    movement = 6
    cost = 13
    researched = False
    unit_type = UnitType.aircraft
    carpet_bombing = True

class Seaplane(Unit):
    attack_roll = 3
    defense_roll  = 3
    movement = 6
    cost = 6
    unit_type = UnitType.aircraft
    # only target transports and subs or convey raid


class Fortification(Unit):
    attack_roll = 0
    defense_roll = 5
    movement = 0
    cost = 10
    unit_type = UnitType.fortification
    first_strike = True
    attack_count = 2
    initial_attack_only = True
    # Buffs all infantry +2 on the first round

SOVIET_UNITS = [
    Militia,
    Infantry,
    AirborneInfantry,
    Marines,
    MountainInfantry,
    Cavalry,
    MotorizedInfantry,
    TankDestroyer,
    LightArmor,
    Artillery,
    SPA,
    AAArtillery,
    Fighter,
    TacticalBomber,
    MediumBomber,
    Seaplane,
    Fortification
]