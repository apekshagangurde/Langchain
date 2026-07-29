import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("currency_converter")

_EXCHANGE_RATE_URL = "https://api.frankfurter.dev/v1/latest"


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another using live exchange rates.

    Uses the free Frankfurter API (no API key required, ECB reference rates).
    Currency codes are 3-letter ISO codes, e.g. "USD", "EUR", "INR", "GBP".

    Args:
        amount: The amount of money to convert.
        from_currency: The 3-letter currency code to convert from.
        to_currency: The 3-letter currency code to convert to.
    """
    from_currency, to_currency = from_currency.upper(), to_currency.upper()

    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            response = client.get(
                _EXCHANGE_RATE_URL,
                params={"amount": amount, "from": from_currency, "to": to_currency},
            )
            response.raise_for_status()
            data = response.json()

        rate = data["rates"].get(to_currency)
        if rate is None:
            return f"Could not find an exchange rate for {to_currency}."
        return f"{amount} {from_currency} = {rate} {to_currency} (rate date: {data['date']})"
    except Exception as exc:
        return f"Error converting currency: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
