@dataclass(frozen=True)
class ObjectiveBounds:
    ideal: tuple[float, float, float]
    reference: tuple[float, float, float]


@dataclass(frozen=True)
class Weights:
    f1: float
    f2: float
    f3: float