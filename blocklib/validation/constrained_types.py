from pydantic.types import ConstrainedInt, ConstrainedFloat


class PositiveInt(ConstrainedInt):
    # These ensure mypy knows what is going on with constrained types
    # Directly using confloat, conint works, but mypy gets unhappy.
    # https://github.com/samuelcolvin/pydantic/issues/239
    ge = 0


class UnitFloat(ConstrainedFloat):
    ge = 0.0
    le = 1.0

