def normalize(value, ideal, reference):
    return (value - ideal) / (reference - ideal)

def normalized_objectives(evaluation, bounds):
    return (
        normalize(evaluation.cost_rs, ...),
        normalize(evaluation.f2_sio2_sq_dev, ...),
        normalize(evaluation.f3_al2o3_sq_dev, ...),
    )