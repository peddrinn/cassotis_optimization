def weighted_sum(evaluation, bounds, weights):
    f1, f2, f3 = normalized_objectives(evaluation, bounds)

    return (
        weights.f1 * f1
        + weights.f2 * f2
        + weights.f3 * f3
    )