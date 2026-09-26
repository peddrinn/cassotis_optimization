from cassotis_optimization.domain import (
    GroupSpec,
    Mineral,
    Pile,
    ProblemInstance,
)
from cassotis_optimization.evaluator import Evaluation, PileQuality
from cassotis_optimization.feasibility import normalized_violation


def _instance() -> ProblemInstance:
    minerals = {
        "M1": Mineral(
            mineral_id="M1",
            price_rs_per_t=100,
            fet_pct=60,
            sio2_pct=5.5,
            al2o3_pct=1.5,
            min_trucks=1,
            max_trucks=4,
            eligible_sinter1=True,
            eligible_sinter2=False,
        )
    }

    groups = {
        "Sinter1": GroupSpec(
            group_id="Sinter1",
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

    piles = {
        "P1": Pile(
            pile_id="P1",
            group_id="Sinter1",
            mass_kt=4.0,
        )
    }

    return ProblemInstance(
        minerals=minerals,
        groups=groups,
        piles=piles,
    )


def test_feasible_solution_has_zero_normalized_violation() -> None:
    instance = _instance()

    evaluation = Evaluation(
        cost_rs=400_000,
        f2_sio2_sq_dev=0.0,
        f3_al2o3_sq_dev=0.0,
        feasible=True,
        violations={},
        quality_by_pile={
            "P1": PileQuality(
                fet_pct=60.0,
                sio2_pct=5.5,
                al2o3_pct=1.5,
            )
        },
        usage_by_mineral={
            "M1": 2,
        },
    )

    violation = normalized_violation(evaluation, instance)

    assert violation.sio2 == 0.0
    assert violation.al2o3 == 0.0
    assert violation.availability_min == 0.0
    assert violation.availability_max == 0.0
    assert violation.total == 0.0


def test_quality_violation_produces_positive_value() -> None:
    instance = _instance()

    evaluation = Evaluation(
        cost_rs=400_000,
        f2_sio2_sq_dev=0.0,
        f3_al2o3_sq_dev=0.0,
        feasible=False,
        violations={"P1:sio2": 0.5},
        quality_by_pile={
            "P1": PileQuality(
                fet_pct=60.0,
                sio2_pct=6.5,
                al2o3_pct=1.5,
            )
        },
        usage_by_mineral={
            "M1": 2,
        },
    )

    violation = normalized_violation(evaluation, instance)

    assert violation.sio2 > 0.0
    assert violation.al2o3 == 0.0
    assert violation.total > 0.0


def test_availability_violation_produces_positive_value() -> None:
    instance = _instance()

    evaluation = Evaluation(
        cost_rs=400_000,
        f2_sio2_sq_dev=0.0,
        f3_al2o3_sq_dev=0.0,
        feasible=False,
        violations={"M1:availability_max": 1.0},
        quality_by_pile={
            "P1": PileQuality(
                fet_pct=60.0,
                sio2_pct=5.5,
                al2o3_pct=1.5,
            )
        },
        usage_by_mineral={
            "M1": 5,
        },
    )

    violation = normalized_violation(evaluation, instance)

    assert violation.availability_max > 0.0
    assert violation.availability_min == 0.0
    assert violation.total > 0.0