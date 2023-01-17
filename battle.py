from typing import List, Tuple
from enum import Enum
from terrains import *
from units import Unit
from dice import d12_less, d12
from itertools import combinations
from dataclasses import dataclass

class BattleResult(Enum):
    attacker_victory = 1
    defender_victory = 2


@dataclass
class RoundResult:
    regular_losses: int
    vehicle_select_losses: int
    ground_naval_losses: int

    def loss_sum(self):
        return self.regular_losses + self.vehicle_select_losses + self.ground_naval_losses

def get_losses(attackers: List[Unit], defenders: List[Unit], terrain: Terrain, *,simulation: bool = False) -> Tuple[RoundResult, RoundResult]:
    """
    Gets number of units that die in a round of combat, does not say which units, but specifies the unit types targetted by target select
    Args:
        attackers (List[Unit]): All attacking units which may fight
        defenders (List[Unit]): All defending which may fight
        simulation (Bool): This attack should not have lasting effects on the battle
    """
    attack_results = RoundResult(0, 0, 0)
    defend_results = RoundResult(0, 0, 0)
    for attacker in attackers:
        attacker.simulation = simulation
        if not attacker.can_attack():
            continue

        attack_value = terrain.modified_attack(attacker, attackers)
        if attack_value <= 1 and attacker.attack_roll >= 1:
            attack_value = 1
        for _ in range(attacker.attack_count):
            if d12_less(attack_value):
                defend_results.regular_losses += 1


    for defender in defenders:
        defender.simulation = simulation
        if not defender.can_attack():
            continue

        defence_value = terrain.modified_defense(defender, defenders)
        if defence_value <= 1 and defender.defense_roll >= 1:
            defence_value = 1

        for _ in range(defender.attack_count):
            if d12_less(terrain.modified_defense(defender, defenders)):
                attack_results.regular_losses += 1

    for attacker in attackers:
        attacker.simulation = False
        attacker.reset_synergy()

    for defender in defenders:
        defender.simulation = False
        defender.reset_synergy()


    return attack_results, defend_results


def objectively_evaluate_armies(attackers: List[Unit], defenders: List[Unit], terrain: Terrain) -> float:
    """
    Generates an objective score which evaluates the effectiveness of the attacking army to cause casualties
    while also weighing its survivalbility
    """
    simulation_results = []
    for _ in range(20):
        attack_losses, defense_losses = get_losses(attackers, defenders, terrain, simulation=True)
        simulation_results.append(attack_losses.loss_sum()-defense_losses.loss_sum())
    return sum(simulation_results)

def get_potential_loss_combinations(units: List[Unit], loss_count: int) -> List[List[Unit]]:
    if len(units) <= loss_count:
        return [units,]

    if loss_count == 0:
        return [[],]

    loss_combinations = []
    for combination in combinations(units, loss_count):
        loss_combinations.append(combination)
    return loss_combinations
    

def loss_selector(attackers: List[Unit], defenders: List[Unit], attacking_losses: int, defending_losses: int, terrain: Terrain) -> Tuple[Unit, Unit]:
    """
    Selects the best units for each side to lose by simulating the effectiveness of each army 

    Takes into account the effect of each possible loss by simulating how effective each army
    is against the other after taking those losses.
    """
    potential_attacker_loss_combinations = get_potential_loss_combinations(attackers, attacking_losses)
    attacker_losses = potential_attacker_loss_combinations.pop()
    best_attacker_loss_score = objectively_evaluate_armies(attacker_losses, defenders, terrain)
    for loss_combination in potential_attacker_loss_combinations:
        attacker_loss_score = objectively_evaluate_armies(loss_combination, defenders, terrain)
        if attacker_loss_score > best_attacker_loss_score:
            best_attacker_loss_score = attacker_loss_score
            attacker_losses = loss_combination

    potential_defender_loss_combinations = get_potential_loss_combinations(defenders, defending_losses)
    defender_losses = potential_defender_loss_combinations.pop()
    best_defender_loss_score = (0 -  objectively_evaluate_armies(attackers, defender_losses, terrain))
    for loss_combination in potential_defender_loss_combinations:
        defender_loss_score = (0 - objectively_evaluate_armies(attackers, loss_combination, terrain))
        if defender_loss_score > best_defender_loss_score:
            best_defender_loss_score = defender_loss_score
            defender_losses = loss_combination

    return attacker_losses, defender_losses

def battle_round_simulation(attacking_targets: List[Unit], defending_targets: List[Unit], attackers: List[Unit], defenders: List[Unit], terrain: Terrain) -> Tuple[Unit, Unit]:
    """
    Simulates a round of fire between targets and casualty selection. Returns all survivors
    Args:
        attacking_targets (List[Unit]): All attacking units which may be targetted by the attack
        defending_targets (List[Unit]): All defending units which may be targetted by the attack
        attackers (List[Unit]): All attacking units which may attack another unit, subset of `attacking_targets`
        defenders (List[Unit]): All defending which may attack another unit, subset of `defending_targets`
    """

    # Get attacks and losses of target-selecting

    # Get attacks and losses of non-target-selecting 
    attacking_loss_count, defending_loss_count = get_losses(attackers, defenders, terrain)
    attacking_losses, defending_losses = loss_selector(attacking_targets, defending_targets, attacking_loss_count.loss_sum(), defending_loss_count.loss_sum(), terrain)
    
    all_attacking_survivors = []
    all_defending_survivors = []

    for attacker in (attacking_targets + attackers):
        if attacker not in attacking_losses and attacker not in all_attacking_survivors:
            all_attacking_survivors.append(attacker)

    for defender in (defending_targets + defenders):
        if defender not in defending_losses and defender not in all_defending_survivors:
            all_defending_survivors.append(defender)

    return all_attacking_survivors, all_defending_survivors



class Battle:
    def __init__(self, attackers: List[Unit], defenders: List[Unit], terrain: Terrain):
        self.original_attackers: List[Unit] = attackers
        self.original_defenders: List[Unit] = defenders

        self.current_attackers: List[Unit] = [x for x in attackers]
        self.current_defenders: List[Unit] = [x for x in defenders]
        self.terrain: Terrain = terrain


    def simulate_battle_round(self, attacking_targets: List[Unit], defending_targets: List[Unit], attackers: List[Unit], defenders: List[Unit]):
        """
        Simulates only a single round of defense/offense
        """
        attacking_survivors, defending_survivors = battle_round_simulation(attacking_targets, defending_targets, attackers, defenders, self.terrain)
        self.current_attackers = attacking_survivors
        self.current_defenders = defending_survivors

    def first_strike(self):
        attackers = [unit for unit in self.current_attackers if unit.first_strike]
        defenders = [unit for unit in self.current_defenders if unit.first_strike]
        self.simulate_battle_round(self.current_attackers, self.current_defenders, attackers, defenders)

    def second_strike(self):
        """
        Now all units _without_ `first_strike` fire
        """
        attackers = [unit for unit in self.current_attackers if not unit.first_strike]
        defenders = [unit for unit in self.current_defenders if not unit.first_strike]
        self.simulate_battle_round(self.current_attackers, self.current_defenders, attackers, defenders)

    def display_sides(self):
        print("ATTACKERS:")
        print(self.current_attackers)
        print("DEFENDERS:")
        print(self.current_defenders)
        print("___________________________")

    def battle(self) -> BattleResult:
        air_battle = all(x.unit_type == UnitType.aircraft for x in self.current_attackers) or all(x.unit_type == UnitType.aircraft for x in self.current_defenders)
        self.display_sides()
        self.first_strike()
        self.second_strike()
        self.display_sides()
        while self.current_attackers and self.current_defenders:
            self.display_sides()
            self.simulate_battle_round(self.current_attackers, self.current_defenders, self.current_attackers, self.current_defenders)

        if self.current_defenders:
            return BattleResult.defender_victory

        if self.current_attackers:
            if air_battle:
                return BattleResult.attacker_victory
            if any(x.unit_type != UnitType.aircraft for x in self.current_attackers):
                return BattleResult.attacker_victory

        return BattleResult.defender_victory