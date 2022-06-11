import numpy as np

from examples.n51sw_dataplate import N51SW
from the_bootstrap_approach.conditions import Conditions
from the_bootstrap_approach.dataplate import DataPlate
from the_bootstrap_approach.performance import bootstrap_cruise_performance_table


def best_angle_of_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine Vx, best rate of climb."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 60, 180, 0.1
    )

    aoc = table[:, 4]
    index_of_highest_aoc = aoc.argmax()
    return table[index_of_highest_aoc]


def best_rate_of_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine Vy, best rate of climb."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 50, 180, 0.1
    )

    roc = table[:, 3]
    index_of_highest_roc = roc.argmax()
    return table[index_of_highest_roc]


def cruise_climb(dataplate: DataPlate, operating_conditions: Conditions):
    """Determine conditions at cruise climb, 100 KIAS."""
    table = bootstrap_cruise_performance_table(
        dataplate, operating_conditions, 100, 101, 1
    )

    return table[0]
