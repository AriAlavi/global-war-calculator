from units import Unit
from typing import List, Dict
from battle import Battle, BattleResult
from terrains import Terrain
import contextlib
import io
from functools import partial
from math import floor

from multiprocessing import Pool
from itertools import combinations

def _simulate_battle_result(attackers: List[Unit], defenders: List[Unit], terrain:Terrain, *args) -> int:
    """
    Helper function to be ran inside of a thread
    """
    with contextlib.redirect_stdout(io.StringIO()): # hide print statement output
        battle = Battle(attackers, defenders, terrain)
        if battle.battle() == BattleResult.attacker_victory:
            return 1
        return 0

def simulate_battle_results(attackers: List[Unit], defenders: List[Unit], terrain:Terrain, n:int=10_000) -> float:
    """
    Simulates the result of an attacker and defender based battle on a specific terrain
    """
    attack_wins = 0
    with Pool(processes=16) as pool:
        part = partial(_simulate_battle_result, attackers, defenders, terrain)
        attack_wins = sum(pool.map(part, range(n)))

    return attack_wins / n

def compare_armies_in_terrain(side_1: List[Unit], side_2: List[Unit], terrain: Terrain, n:int=20_000) -> float:
    """
    Simulates the general results of battles (both attack and defensive) in general
    """
    battle_type_1_results = simulate_battle_results(side_1, side_2, terrain, int(n/2))
    battle_type_2_results = 1 - simulate_battle_results(side_2, side_1, terrain, int(n/2))
    return (battle_type_1_results + battle_type_2_results) / 2


def get_all_legal_unit_builds(available_units: List[Unit], money: int) -> List[List[Unit]]:
    """
    Extremely laggy just to generate the legal builds once money >= 9
    
    Creating a battle between each one of these will be worse.
    Look for an AI-based solution or maybe ELO scoring system?
    """
    if money <= 0:
        return []

    affordable_available_units: List[Unit] = []
    for unit in available_units:
        if unit.cost <= money:
            affordable_available_units.append(unit)

    if not affordable_available_units:
        return []

    if len(affordable_available_units) == 1:
        afford_count = money / affordable_available_units[0].cost
        return [{
            affordable_available_units[0]: afford_count
        }]

    complete_max_army:List[Unit] = []

    for available_unit in affordable_available_units:
        can_afford_max = floor(money/available_unit.cost)
        complete_max_army.extend([available_unit] * can_afford_max)

    cheapest_unit_cost = min([x.cost for x in available_units])


    legal_build_items = set()

    for i in range(len(complete_max_army)):
        for combination in combinations(complete_max_army, i):
            if combination in legal_build_items:
                continue
            total_cost = sum([x.cost for x in combination])
            if total_cost <= money < total_cost + cheapest_unit_cost:
                legal_build_items.add(combination)

    return legal_build_items
    