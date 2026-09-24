from pathlib import Path

from cassotis_optimization.io import load_instance
from cassotis_optimization.validation import validate_instance


def main() -> None:
    data_dir = Path("data/example_instance")
    instance = load_instance(data_dir)
    errors = validate_instance(instance)

    print(f"Minerals: {len(instance.minerals)}")
    print(f"Groups: {len(instance.groups)}")
    print(f"Piles: {len(instance.piles)}")
    print(f"Required trucks: {sum(p.n_trucks for p in instance.piles.values())}")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nInstance validation: OK")


if __name__ == "__main__":
    main()
