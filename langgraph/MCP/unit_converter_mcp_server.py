from mcp.server.fastmcp import FastMCP

mcp = FastMCP("unit_converter")

_LENGTH_TO_METERS = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "mile": 1609.344,
    "yard": 0.9144,
    "foot": 0.3048,
    "inch": 0.0254,
}

_WEIGHT_TO_KG = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.45359237,
    "ounce": 0.028349523125,
}


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == "celsius":
        celsius = value
    elif from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")

    if to_unit == "celsius":
        return celsius
    if to_unit == "fahrenheit":
        return celsius * 9 / 5 + 32
    if to_unit == "kelvin":
        return celsius + 273.15
    raise ValueError(f"Unknown temperature unit: {to_unit}")


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a numeric value between common length, weight, or temperature units.

    Length units: m, km, cm, mm, mile, yard, foot, inch.
    Weight units: kg, g, mg, lb, ounce.
    Temperature units: celsius, fahrenheit, kelvin.
    Units on both sides must belong to the same category (e.g. don't mix length with weight).

    Args:
        value: The numeric value to convert.
        from_unit: The unit `value` is currently in.
        to_unit: The unit to convert `value` into.
    """
    from_unit, to_unit = from_unit.lower(), to_unit.lower()

    try:
        if from_unit in _LENGTH_TO_METERS and to_unit in _LENGTH_TO_METERS:
            meters = value * _LENGTH_TO_METERS[from_unit]
            result = meters / _LENGTH_TO_METERS[to_unit]
        elif from_unit in _WEIGHT_TO_KG and to_unit in _WEIGHT_TO_KG:
            kilograms = value * _WEIGHT_TO_KG[from_unit]
            result = kilograms / _WEIGHT_TO_KG[to_unit]
        elif from_unit in ("celsius", "fahrenheit", "kelvin") and to_unit in (
            "celsius",
            "fahrenheit",
            "kelvin",
        ):
            result = _convert_temperature(value, from_unit, to_unit)
        else:
            return (
                f"Cannot convert from '{from_unit}' to '{to_unit}' — "
                "unsupported or mismatched unit category."
            )
        return f"{value} {from_unit} = {round(result, 4)} {to_unit}"
    except Exception as exc:
        return f"Error converting units: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
