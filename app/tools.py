import random
from datetime import datetime

import httpx
from strands import tool


@tool
async def get_weather(location: str) -> str:
    """Get current weather for a location."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://wttr.in/{location}",
            params={"format": "3"},
            headers={"User-Agent": "strandsagent/1.0"},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.text.strip()


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def convert_temperature(celsius: float) -> str:
    """Convert a Celsius value to Fahrenheit and return a labelled string.

    Pure math — no I/O, always fast, always deterministic.
    Useful for multi-step chains: get_weather returns Celsius, the model then
    calls this to give the user both units in its final answer.
    Example: convert_temperature(22.0) -> "22.0°C is 71.6°F"
    """
    fahrenheit = celsius * 9 / 5 + 32
    return f"{celsius}°C is {fahrenheit:.1f}°F"


@tool
def roll_dice(sides: int = 6, count: int = 1) -> str:
    """Roll one or more dice with the given number of sides.

    Example: roll_dice(sides=20, count=2) rolls two 20-sided dice.
    """
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    return f"Rolled {count}d{sides}: {rolls} — total: {total}"


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a ticker symbol (simulated data)."""
    base_prices = {
        "AAPL": 189.0,
        "GOOGL": 175.0,
        "MSFT": 415.0,
        "AMZN": 195.0,
        "TSLA": 245.0,
        "NVDA": 875.0,
    }
    base = base_prices.get(symbol.upper(), 100.0)
    price = round(base * random.uniform(0.95, 1.05), 2)
    change = round(price - base, 2)
    sign = "+" if change >= 0 else ""
    return f"{symbol.upper()}: ${price} ({sign}{change})"


@tool
def flip_coin(count: int = 1) -> str:
    """Flip one or more coins and return the results."""
    results = [random.choice(["Heads", "Tails"]) for _ in range(count)]
    heads = results.count("Heads")
    tails = results.count("Tails")
    return f"Results: {', '.join(results)} — Heads: {heads}, Tails: {tails}"


@tool
def get_fun_fact(topic: str = "general") -> str:
    """Return a fun fact about the given topic."""
    facts = {
        "space": "A day on Venus is longer than a year on Venus — it takes 243 Earth days to rotate once but only 225 Earth days to orbit the Sun.",
        "animals": "Octopuses have three hearts, nine brains, and blue blood.",
        "food": "Honey never spoils — archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible.",
        "math": "If you shuffle a deck of cards properly, the exact order has almost certainly never existed before in history.",
        "history": "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "general": "A group of flamingos is called a flamboyance.",
    }
    return facts.get(topic.lower(), facts["general"])


@tool
def calculate_tip(
    bill_amount: float, tip_percent: float = 18.0, people: int = 1
) -> str:
    """Calculate the tip and total for a restaurant bill, optionally split among people."""
    tip = round(bill_amount * tip_percent / 100, 2)
    total = round(bill_amount + tip, 2)
    per_person = round(total / people, 2)
    result = f"Bill: ${bill_amount:.2f} | Tip ({tip_percent}%): ${tip:.2f} | Total: ${total:.2f}"
    if people > 1:
        result += f" | Per person ({people}): ${per_person:.2f}"
    return result
