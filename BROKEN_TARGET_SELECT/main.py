import units as Unit
from battle import Battle
import terrains as Terrain
from battle_statistics import compare_armies_in_terrain, simulate_battle_results, get_all_legal_unit_builds


def main():
    # attackers = [
    #     Unit.TacticalBomber(),
    #     Unit.TacticalBomber(),
    #     Unit.TankDestroyer(),
    #     Unit.Infantry(),
    #     Unit.Infantry(),
    #     Unit.Infantry(),
    # ]
    # defenders = [
    #     Unit.Infantry(),
    #     Unit.Infantry(),
    #     Unit.Infantry(),
    #     Unit.MediumArmor(),
    #     Unit.MediumArmor(),
    #     Unit.MediumArmor(),
    # ]
    attackers = [
        Unit.Infantry(),
        Unit.Infantry(),
        Unit.TankDestroyer(),
        Unit.TankDestroyer(),
    ]
    defenders = [
        Unit.Infantry(),
        Unit.Infantry(),
        Unit.MediumArmor(),
        Unit.MediumArmor(),
    ]
    # b = Battle(attackers, defenders, Terrain.Basic)
    # print(b.battle())
    print(simulate_battle_results(attackers, defenders, Terrain.Basic))
    # print(compare_armies_in_terrain(attackers, defenders, Terrain.Basic))
    # print(get_all_legal_unit_builds([Unit.Militia, Unit.Infantry, Unit.Cavalry, Unit.Artillery], 20))

if __name__ == "__main__":
    main()