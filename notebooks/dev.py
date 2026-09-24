from cassotis_optimization.algorithms.constructive import (
    construct_initial_solution,
)
from cassotis_optimization.evaluator import evaluate
from cassotis_optimization.io import load_instance

instance = load_instance("data/example_instance")

solution = construct_initial_solution(instance)

evaluation = evaluate(solution, instance)

print("Feasible:", evaluation.feasible)
print("Cost:", evaluation.cost_rs)
print("f2:", evaluation.f2_sio2_sq_dev)
print("f3:", evaluation.f3_al2o3_sq_dev)
print("Violations:", evaluation.violations)