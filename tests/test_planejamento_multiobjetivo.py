import json
from pathlib import Path
import pytest
from cassotis_optimization.multiobjective.multiobjective import EpsilonLimits, Weights
from cassotis_optimization.multiobjective.planejamento import epsilon_grid, weight_grid
PROTOCOL=Path(__file__).resolve().parents[1]/"data/protocolo_entrega2.json"
def test_weight_grid():
    grid=weight_grid(4,include_equal_weights=True)
    assert len(grid)==16 and len(set(grid))==16
    for weights in grid:assert sum((weights.f1,weights.f2,weights.f3))==pytest.approx(1.0)
    for w in (Weights(1,0,0),Weights(0,1,0),Weights(0,0,1),Weights(1/3,1/3,1/3)):assert w in grid
def test_weight_grid_without_center():assert len(weight_grid(4,include_equal_weights=False))==15
def test_epsilon_grid():
    levels=(0.25,0.5,0.75,1.0);grid=epsilon_grid(levels,levels)
    assert len(grid)==16 and len(set(grid))==16
    assert EpsilonLimits(0.25,0.25) in grid
    assert EpsilonLimits(1,1) in grid
def test_experiment_protocol():
    p=json.loads(PROTOCOL.read_text(encoding="utf8"))
    w=weight_grid(p["weighted_sum"]["simplex_denominator"],p["weighted_sum"]["include_equal_weights"])
    e=epsilon_grid(p["epsilon_restricted"]["levels_f2"],p["epsilon_restricted"]["levels_f3"])
    assert len(w)==p["weighted_sum"]["expected_configurations"]==16
    assert len(e)==p["epsilon_restricted"]["expected_configurations"]==16
    pilot_seeds=p["pilot"]["seeds"];final_seeds=p["final"]["seeds"]
    assert len(final_seeds)==5 and len(set(final_seeds))==5
    assert set(pilot_seeds).isdisjoint(final_seeds)
    assert set(final_seeds).isdisjoint(range(2016,2021))
    assert len(w)*len(final_seeds)*p["final"]["max_evaluations"]==16_000_000
    assert len(e)*len(final_seeds)*p["final"]["max_evaluations"]==16_000_000
@pytest.mark.parametrize('levels',[((),(.5,)),((.5,),())])
def test_empty_epsilon_grids(levels):
    with pytest.raises(ValueError):epsilon_grid(*levels)
