from cassotis_optimization.multiobjective.pareto import dominates, nondominated_indices


def test_dominance_uses_three_objectives():
    rows = [
        {"f1": 1, "f2": 1, "f3": 1},
        {"f1": 2, "f2": 2, "f3": 2},
        {"f1": 0, "f2": 3, "f3": 1},
        {"f1": 3, "f2": 0, "f3": 1},
    ]
    assert dominates(rows[0], rows[1])
    assert not dominates(rows[0], rows[2])
    assert nondominated_indices(rows) == [0, 2, 3]


def test_projected_dominance_is_not_three_dimensional():
    # Primeiro ponto domina em f1,f2, mas perde em f3.
    points = [{"f1": 1, "f2": 1, "f3": 9}, {"f1": 2, "f2": 2, "f3": 0}]
    assert nondominated_indices(points) == [0, 1]


def test_equal_points_remain_available_for_provenance():
    points = [{"f1": 1, "f2": 1, "f3": 1}, {"f1": 1, "f2": 1, "f3": 1}]
    assert nondominated_indices(points) == [0, 1]
