def epsilon_objective(evaluation, bounds):
    # objetivo principal = custo
    f1, _, _ = normalized_objectives(evaluation, bounds)
    return f1

def epsilon_violations(evaluation, bounds, epsilon2, epsilon3):
    _, f2, f3 = normalized_objectives(evaluation, bounds)

    v2 = max(0.0, f2 - epsilon2)
    v3 = max(0.0, f3 - epsilon3)

    return v2, v3