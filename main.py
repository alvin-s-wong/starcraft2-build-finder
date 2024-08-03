# %% [markdown]
# # Starcraft 2 Build Finder
# 
# This notebook is to discover the most optimized build order to maximize total army composition DPS for a given time target.
# 
# We are only focused on Protoss build orders for this code.

# %%
import random
import copy
from pprint import pprint

TARGET_TIME = 1800  # Evaluate at 5 minutes (300 seconds)

# Constants for unit costs and build times
UNIT_COSTS = {
    # Units
    "probe": {"minerals": 50, "gas": 0, "time": 12, "supply": 1},
    "zealot": {"minerals": 100, "gas": 0, "time": 38, "supply": 2},
    "stalker": {"minerals": 125, "gas": 50, "time": 42, "supply": 2},
    "sentry": {"minerals": 50, "gas": 100, "time": 37, "supply": 2},
    "adept": {"minerals": 100, "gas": 25, "time": 27, "supply": 2},
    "high_templar": {"minerals": 50, "gas": 150, "time": 39, "supply": 2},
    "dark_templar": {"minerals": 125, "gas": 125, "time": 39, "supply": 2},
    "archon": {
        "minerals": 0,
        "gas": 0,
        "time": 9,
        "supply": 4,
    },  # Archon morphs from High/Dark Templar
    "observer": {"minerals": 25, "gas": 75, "time": 21, "supply": 1},
    "immortal": {"minerals": 275, "gas": 100, "time": 39, "supply": 4},
    "warp_prism": {"minerals": 200, "gas": 0, "time": 36, "supply": 2},
    "colossus": {"minerals": 300, "gas": 200, "time": 54, "supply": 6},
    "disruptor": {"minerals": 150, "gas": 150, "time": 36, "supply": 3},
    "phoenix": {"minerals": 150, "gas": 100, "time": 25, "supply": 2},
    "void_ray": {"minerals": 250, "gas": 150, "time": 43, "supply": 4},
    "oracle": {"minerals": 150, "gas": 150, "time": 37, "supply": 3},
    "tempest": {"minerals": 300, "gas": 200, "time": 43, "supply": 6},
    "carrier": {"minerals": 350, "gas": 250, "time": 64, "supply": 6},
    "mothership": {
        "minerals": 400,
        "gas": 400,
        "time": 114,
        "supply": 8,
    },  # Requires Nexus upgrade
    # Buildings
    "pylon": {"minerals": 100, "gas": 0, "time": 18, "supply": 8},
    "gateway": {"minerals": 150, "gas": 0, "time": 46, "supply": 0},
    "assimilator": {"minerals": 75, "gas": 0, "time": 21, "supply": 0},
    "cybernetics_core": {"minerals": 150, "gas": 0, "time": 36, "supply": 0},
    "forge": {"minerals": 150, "gas": 0, "time": 32, "supply": 0},
    "photon_cannon": {"minerals": 150, "gas": 0, "time": 29, "supply": 0},
    "shield_battery": {"minerals": 100, "gas": 0, "time": 29, "supply": 0},
    "twilight_council": {"minerals": 150, "gas": 100, "time": 36, "supply": 0},
    "robotics_facility": {"minerals": 200, "gas": 100, "time": 46, "supply": 0},
    "robotics_bay": {"minerals": 150, "gas": 100, "time": 46, "supply": 0},
    "stargate": {"minerals": 150, "gas": 150, "time": 43, "supply": 0},
    "fleet_beacon": {"minerals": 300, "gas": 200, "time": 43, "supply": 0},
    "templar_archives": {"minerals": 150, "gas": 200, "time": 36, "supply": 0},
    "dark_shrine": {"minerals": 150, "gas": 150, "time": 71, "supply": 0},
    "nexus": {"minerals": 400, "gas": 0, "time": 71, "supply": 15},
}

# DPS values for Protoss units against light units (updated)
UNIT_DPS = {
    "zealot": 16,
    "stalker": 13.85,
    "sentry": 6.67,
    "high_templar": 0,  # High Templars use Psionic Storm, which deals 80 damage over 2.85 seconds
    "dark_templar": 45,
    "archon": 23.81,
    "adept": 11.11,
    "phoenix": 16.67,
    "void_ray": 9.72,
    "oracle": 22.22,
    "carrier": 5 * 16,  # Interceptors deal 5 DPS each, with up to 8 interceptors
    "tempest": 11.29,
    "colossus": 23.21,
    "disruptor": 0,  # Disruptors use Purification Nova, which deals 155 damage over 2 seconds
    "mothership": 23.81,  # Same as the Archon
    "probe": 5,
}

# Prerequisites for each unit and building
PREREQUISITES = {
    # Units
    "probe": ["nexus"],
    "zealot": ["gateway"],
    "stalker": ["gateway", "cybernetics_core"],
    "sentry": ["gateway", "cybernetics_core"],
    "adept": ["gateway", "cybernetics_core"],
    "high_templar": ["gateway", "cybernetics_core", "templar_archives"],
    "dark_templar": ["gateway", "cybernetics_core", "dark_shrine"],
    "archon": [
        "high_templar",
        "dark_templar",
    ],  # Requires merging of two high or dark templars
    "observer": ["robotics_facility"],
    "immortal": ["robotics_facility"],
    "warp_prism": ["robotics_facility"],
    "colossus": ["robotics_facility", "robotics_bay"],
    "disruptor": ["robotics_facility", "robotics_bay"],
    "phoenix": ["stargate"],
    "void_ray": ["stargate"],
    "oracle": ["stargate"],
    "tempest": ["stargate", "fleet_beacon"],
    "carrier": ["stargate", "fleet_beacon"],
    "mothership": ["nexus", "fleet_beacon"],  # Requires Nexus upgrade
    # Buildings
    "pylon": ["nexus"],
    "gateway": ["nexus"],
    "assimilator": ["nexus"],
    "cybernetics_core": ["gateway"],
    "forge": ["nexus"],
    "photon_cannon": ["forge"],
    "shield_battery": ["gateway"],
    "twilight_council": ["cybernetics_core"],
    "robotics_facility": ["cybernetics_core"],
    "robotics_bay": ["robotics_facility"],
    "stargate": ["cybernetics_core"],
    "fleet_beacon": ["stargate"],
    "templar_archives": ["twilight_council"],
    "dark_shrine": ["twilight_council"],
    "nexus": [],
}

# %% [markdown]
# Now we create a Game State class for the "engine" of SC2 simulated.

# %%
class GameState:
    def __init__(self):
        self.resources = {"minerals": 300, "gas": 200}
        self.units = {"probe": 22}
        self.buildings = {
            "nexus": 1,
            "pylon": 3,
            "gateway": 1,
            "cybernetics_core": 1,
            "warp_gate": 1,
            "assimilator": 2,
        }
        self.time = 180
        self.build_queue = []
        self.production_queues = {
            "gateway": [],
            "warp_gate": [],
            "robotics_facility": [],
        }
        self.supply = 22
        self.supply_max = 24

    def can_build(self, unit):

        if not (
            self.resources["minerals"] >= UNIT_COSTS[unit]["minerals"]
            and self.resources["gas"] >= UNIT_COSTS[unit]["gas"]
            and self.supply + UNIT_COSTS[unit]["supply"] <= self.supply_max
        ):
            return False

        if unit in PREREQUISITES:
            for prerequisite in PREREQUISITES[unit]:
                print(f'Checking if {unit} has prerequisite building{PREREQUISITES[unit]}')
                if self.buildings.get(prerequisite, 0) <= 0:
                    print("Nope")
                    return False
                else:
                    print("Pre-requisite met: OK")
        
        return True

    def build_unit(self, unit):
        if self.can_build(unit):
            self.resources["minerals"] -= UNIT_COSTS[unit]["minerals"]
            self.resources["gas"] -= UNIT_COSTS[unit]["gas"]
            if unit in ["zealot", "stalker", "sentry", "adept"]:
                self.production_queues["gateway"].append(
                    (unit, self.time + UNIT_COSTS[unit]["time"])
                )
                print(
                    f'Added {unit} to gateway production queue. Now: {self.production_queues["gateway"]}'
                )

            else:
                self.build_queue.append((unit, self.time + UNIT_COSTS[unit]["time"]))
                print(
                    f'Added {unit} to instant (warpgate) production. Now: {self.production_queues["gateway"]}'
                )

    def step(self, action):
        if action in UNIT_COSTS:
            self.build_unit(action)

        self.time += 1

        completed_units = []

        # Check for completed buildings and units in the build queue
        for unit, completion_time in self.build_queue:
            if self.time >= completion_time:
                completed_units.append((unit, completion_time))

        for unit, _ in completed_units:
            self.build_queue.remove((unit, _))
            if unit in self.units:
                self.units[unit] += 1
            else:
                self.units[unit] = 1

            print(f"Added completed unit:{unit}")

            if unit in self.buildings:
                self.buildings[unit] += 1
            else:
                self.buildings[unit] = 1

            if unit in UNIT_COSTS:
                self.supply += UNIT_COSTS[unit]["supply"]

            if unit == "pylon":
                self.supply_max += 8

            if unit == "gateway":
                self.production_queues["gateway"] = []

            if unit == "warp_gate":
                self.buildings["gateway"] -= 1
                self.buildings["warp_gate"] += 1
                self.production_queues["warp_gate"] = self.production_queues.pop(
                    "gateway", []
                )

        # Check for completed units in the production queues
        for building, queue in self.production_queues.items():
            for i in range(len(queue)):
                unit, completion_time = queue[i]
                if self.time >= completion_time:
                    self.units[unit] = self.units.get(unit, 0) + 1
                    self.production_queues[building].pop(i)
                    break

        # Simulate resource collection
        self.resources["minerals"] += (
            self.units["probe"] * 0.7
        )  # Assume each probe gathers 0.7 minerals per second
        self.resources["gas"] += (
            self.units.get("assimilator", 0) * 0.2
        )  # Assume each assimilator produces 0.2 gas per second

# %% [markdown]
# # Supply Calculator
# 
# This function helps find the total supply given the list of units.

# %%
def calculate_total_supply(units):
    total_supply = 0
    for k, v in units.items():
        total_supply += UNIT_COSTS[k]["supply"] * v
    return total_supply


# %% [markdown]
# # Army DPS Calculator
# 
# This function helps find the total army DPS given the list of units.

# %%
def calculate_total_dps(units):
    total_dps = 0
    for k, v in units.items():
        if UNIT_DPS.get(k) is not None:
            total_dps += UNIT_DPS.get(k) * v
    return total_dps

# %% [markdown]
# ## The Simulator!
# 
# This is the primary function that will step through and evaluate a proposed build order and target time

# %%
def evaluate_build_order(build_order, target_time):
    state = GameState()
    for action in build_order:
        if action in UNIT_COSTS:
            duration = UNIT_COSTS[action]["time"]
        else:
            duration = 1  # default duration if not specified
        print(f"Time: {state.time}, Action: {action}, Duration: {duration}")
        for _ in range(duration):
            state.step(action)
            if state.time >= target_time:
                break
        if state.time >= target_time:
            break
    total_dps = calculate_total_dps(state.units)
    total_supply = calculate_total_supply(state.units)
    units = copy.deepcopy(state.units)
    results = {"total_dps": total_dps, "total_supply": total_supply, "state_units": units}
    return results

# %% [markdown]
# ## Build order unit/building randomizer
# 
# Based on units/buildings to consider for the build.  Helps for what unit composition you want.

# %%
def generate_random_build_order():
    actions = [
        "probe",
        "pylon",
        "gateway",
        "zealot",
        "stalker",
        "robotics_bay",
        "immortal",
    ]
    return random.choices(
        actions, k=40
    )  # Generate a random build order with 20 actions

# %% [markdown]
# ## Mutations
# 
# We are finding which random amount of each to build.

# %%

def mutate(build_order):
    actions = [
        "probe",
        "pylon",
        "gateway",
        "zealot",
        "stalker",
        "robotics_bay",
        "immortal",
    ]
    index = random.randint(0, len(build_order) - 1)
    build_order[index] = random.choice(actions)
    return build_order

# %% [markdown]
# ## Crossover
# 
# To mash up and crossover two build orders

# %%
def crossover(build_order1, build_order2):
    index = random.randint(0, len(build_order1) - 1)
    new_build_order = build_order1[:index] + build_order2[index:]
    return new_build_order



# %% [markdown]
# # Put it all Together!
# 
# Let's search for the optimal(based on DPS total) build order for a given target time.

# %%

def search_optimal_build_order(target_time):
    population_size = 20
    generations = 50
    mutation_rate = 0.1

    population = [generate_random_build_order() for _ in range(population_size)]

    for _ in range(generations):
        population = sorted(
            population,
            key=lambda order: -evaluate_build_order(order, target_time)["total_dps"],
        )
        new_population = population[:2]  # Keep top 2

        while len(new_population) < population_size:
            if random.random() < mutation_rate:
                new_population.append(mutate(random.choice(population)))
            else:
                new_population.append(
                    crossover(random.choice(population), random.choice(population))
                )

        population = new_population

    best_build_order = population[0]
    best_score_results = evaluate_build_order(best_build_order, target_time)
    return best_build_order, best_score_results



# %% [markdown]
# # Report the Results!
# 
# Let's see what build orders we come up with!

# %%

optimal_build_order, best_score_results = search_optimal_build_order(TARGET_TIME)
print("Optimal Build Order:\n")
for entry in optimal_build_order:
    print(f"- {entry}")
print("\n")
print("Best Score (Total DPS):", best_score_results)

# %%



