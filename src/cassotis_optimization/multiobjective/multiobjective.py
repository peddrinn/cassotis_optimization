
from dataclasses import dataclass
from math import isclose, isfinite


@dataclass(frozen=True)
class ObjectiveBounds:
    ideal: tuple[float, float, float]
    reference: tuple[float, float, float]

    def __post_init__(self) -> None:
        if len(self.ideal) != 3 or len(self.reference) != 3:
            raise ValueError("São necessários três valores por vetor.")

        if not all(isfinite(v) for v in (*self.ideal, *self.reference)):
            raise ValueError("As referências devem ser finitas.")

        if any(ref <= ideal for ideal, ref in zip(self.ideal, self.reference)):
            raise ValueError("Cada referência superior deve superar o ideal.")



@dataclass(frozen=True)
class Weights:
    f1: float
    f2: float
    f3: float

    def __post_init__(self) -> None:
        values = (self.f1, self.f2, self.f3)

        if not all(isfinite(value) for value in values):
            raise ValueError("Os pesos devem ser finitos.")

        if any(value < 0 for value in values):
            raise ValueError("Os pesos não podem ser negativos.")

        if not isclose(
            sum(values),
            1.0,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError("A soma dos pesos deve ser igual a 1.")
