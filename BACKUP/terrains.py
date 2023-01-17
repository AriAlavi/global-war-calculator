from units import *
from typing import List

class Terrain:
    @classmethod
    def modified_attack(cls, unit: Unit, friendlies: List[Unit]) -> int:
        """
        Gets the attack of the unit when terrain is taken into consideration
        """
        return unit.get_attack(friendlies)

    @classmethod
    def modified_defense(cls, unit: Unit, friendlies: List[Unit]) -> int:
        """
        Gets the defense of the unit when terrain is taken into consideration
        """
        return unit.get_defense(friendlies)

class Basic(Terrain):
    ...


# Artillery does not suffer terrain penality
# Rivers are a minus one only on the first turn for the attacker and do not stack buffs/debuffs with other terrain, follow the rules below

# Terrain works in that you take the worst peanlity and best buff when there is multiple
# terrain in a battle
class Desert(Terrain):
    @classmethod
    def modified_attack(cls, unit: Unit, friendlies: List[Unit]) -> int:
        if unit.unit_type == UnitType.aircraft:
            return unit.get_attack(friendlies)
        return unit.get_attack(friendlies) - 1

class Mountain(Terrain):
    @classmethod
    def modified_attack(cls, unit: Unit, friendlies: List[Unit]) -> int:
        if isinstance(unit, MountainInfantry) or unit.unit_type == UnitType.aircraft:
            return unit.get_attack(friendlies)
        return unit.get_attack(friendlies) - 1

    @classmethod
    def modified_defense(cls, unit: Unit, friendlies: List[Unit]) -> int:
        if isinstance(unit, MountainInfantry):
            return unit.get_defense(friendlies) + 1
        return unit.get_defense(friendlies)

class Marsh(Terrain):
    @classmethod
    def modified_attack(cls, unit: Unit, friendlies: List[Unit]) -> int:
        """
        Gets the attack of the unit when terrain is taken into consideration
        """
        if unit.unit_type == UnitType.vehicle:
            return unit.get_attack(friendlies) - 2
        return unit.get_attack(friendlies)

    @classmethod
    def modified_defense(cls, unit: Unit, friendlies: List[Unit]) -> int:
        """
        Gets the attack of the unit when terrain is taken into consideration
        """
        if unit.unit_type == UnitType.vehicle:
            return unit.get_defense(friendlies) - 2
        return unit.get_defense(friendlies)


class Jungle(Marsh):
    ...

class City(Terrain):
    @classmethod
    def modified_defense(cls, unit: Unit, friendlies: List[Unit]) -> int:
        # Infantry in cities that are defending get a level 1 target select against vehicles
        if unit.unit_type == UnitType.infantry:
            return unit.get_defense(friendlies) + 1
        return unit.get_defense(friendlies) 

class SurroundedCity(Terrain):
    @classmethod
    def modified_defense(cls, unit: Unit, friendlies: List[Unit]) -> int:
        return unit.get_defense(friendlies) - 1

TERRAIN_TYPES = [Basic, Mountain, Marsh, Jungle, City, SurroundedCity]