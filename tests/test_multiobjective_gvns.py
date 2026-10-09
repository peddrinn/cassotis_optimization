from pathlib import Path

import pytest

from cassotis_optimization.algorithms.gvns import CountingEvaluator, GVNSConfig, run_gvns
from cassotis_optimization.feasibility import normalized_violation
from cassotis_optimization.io import load_instance
from cassotis_optimization.multiobjective.epsilon_restrito import (
    epsilon_objective,
    epsilon_violations,
)
from cassotis_optimization.multiobjective.multiobjective import EpsilonLimits, Weights
from cassotis_optimization.multiobjective.normalizacao import load_bounds
from cassotis_optimization.multiobjective.soma_ponderada import weighted_sum

ROOT=Path(__file__).resolve().parents[1]
REFERENCE_FILE=ROOT/"data/referencias_multiobjetivo.json"
INSTANCE_DIR=ROOT/"data/example_instance"
@pytest.fixture(scope="module")
def example():
    instance=load_instance(INSTANCE_DIR)
    bounds=load_bounds(REFERENCE_FILE)
    result=run_gvns(instance,GVNSConfig(objective="f1",seed=0,max_evaluations=4000))
    assert result.best.evaluation.feasible
    return instance,bounds,result.best.solution

def test_weighted_sum_score(example):
    instance,bounds,solution=example
    weights=Weights(0.5,0.25,0.25)
    config=GVNSConfig(objective="weighted_sum",bounds=bounds,weights=weights)
    candidate=CountingEvaluator(instance,config)(solution)
    assert candidate.feasible
    assert candidate.objective==pytest.approx(weighted_sum(candidate.evaluation,bounds,weights))

def test_epsilon_changes_search_feasibility(example):
    instance,bounds,solution=example
    wide=CountingEvaluator(instance,GVNSConfig(objective="epsilon_restricted",bounds=bounds,epsilon_limits=EpsilonLimits(10,10)))(solution)
    assert wide.evaluation.feasible and wide.feasible
    tight_limits=EpsilonLimits(-10,-10)
    tight=CountingEvaluator(instance,GVNSConfig(objective="epsilon_restricted",bounds=bounds,epsilon_limits=tight_limits))(solution)
    assert tight.evaluation.feasible and not tight.feasible
    v2,v3=epsilon_violations(tight.evaluation,bounds,tight_limits)
    original=normalized_violation(tight.evaluation,instance).total
    assert tight.violation==pytest.approx(original+v2+v3)
    assert tight.objective==pytest.approx(epsilon_objective(tight.evaluation,bounds))

def test_invalid_multiobjective_config():
    for objective in ("weighted_sum","epsilon_restricted","unknown"):
        with pytest.raises(ValueError):GVNSConfig(objective=objective)

@pytest.mark.parametrize("mode",("weighted_sum","epsilon_restricted"))
def test_multiobjective_run_respects_budget(mode):
    instance=load_instance(INSTANCE_DIR);bounds=load_bounds(REFERENCE_FILE)
    args={"objective":mode,"bounds":bounds,"seed":3,"max_evaluations":1000,"sample_size":250}
    if mode=="weighted_sum":args["weights"]=Weights(0.5,0.25,0.25)
    else:args["epsilon_limits"]=EpsilonLimits(0.75,0.75)
    result=run_gvns(instance,GVNSConfig(**args))
    assert result.evaluations==1000 and result.best is not None and result.best.violation>=0
