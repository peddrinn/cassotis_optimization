from cassotis_optimization.domain import GroupSpec, Mineral, Pile, ProblemInstance
from cassotis_optimization.evaluator import evaluate
from cassotis_optimization.solution import Solution


def _synthetic_instance() -> ProblemInstance:
    minerals = {
        "A": Mineral("A", 100, 60, 5.0, 1.0, 0, 1, True, False),
        "B": Mineral("B", 200, 62, 6.0, 2.0, 0, 1, True, False),
    }
    groups = {
        "Sinter1": GroupSpec(
            "Sinter1",
            fet_min=0,
            fet_target=None,
            fet_max=100,
            sio2_min=5.0,
            sio2_target=5.5,
            sio2_max=6.0,
            al2o3_min=1.0,
            al2o3_target=1.5,
            al2o3_max=2.0,
        )
    }
    piles = {"P1": Pile("P1", "Sinter1", 4.0)}
    return ProblemInstance(minerals=minerals, groups=groups, piles=piles)


def test_evaluator_computes_cost_quality_and_objectives() -> None:
    instance = _synthetic_instance()
    solution = Solution({"P1": ("A", "B")})

    result = evaluate(solution, instance)

    assert result.feasible
    assert result.cost_rs == 600_000
    assert result.quality_by_pile["P1"].sio2_pct == 5.5
    assert result.quality_by_pile["P1"].al2o3_pct == 1.5
    assert result.f2_sio2_sq_dev == 0.0
    assert result.f3_al2o3_sq_dev == 0.0


def test_evaluator_detects_global_availability_violation() -> None:
    instance = _synthetic_instance()
    solution = Solution({"P1": ("A", "A")})

    result = evaluate(solution, instance)

    assert not result.feasible
    assert result.violations["A:availability_max"] == 1.0
