from cassotis_optimization.evaluator import Evaluation
from cassotis_optimization.objectives import objective_value


def test_objective_selector() -> None:
    evaluation = Evaluation(
        cost_rs=1000.0,
        f2_sio2_sq_dev=2.5,
        f3_al2o3_sq_dev=0.8,
        feasible=True,
        violations={},
        quality_by_pile={},
        usage_by_mineral={},
    )

    assert objective_value(evaluation, "f1") == 1000.0
    assert objective_value(evaluation, "f2") == 2.5
    assert objective_value(evaluation, "f3") == 0.8