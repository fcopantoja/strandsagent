from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tools import (
    calculate_tip,
    convert_temperature,
    flip_coin,
    get_current_time,
    get_fun_fact,
    get_stock_price,
    get_weather,
    roll_dice,
)

# --- get_weather ---


def _make_weather_mock(text: str) -> MagicMock:
    mock_response = MagicMock()
    mock_response.text = text
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.asyncio
async def test_get_weather_returns_response():
    with patch(
        "app.tools.httpx.AsyncClient",
        return_value=_make_weather_mock("Madrid: ☀️ +22°C"),
    ):
        result = await get_weather("madrid")
    assert "Madrid" in result or "22" in result


@pytest.mark.asyncio
async def test_get_weather_strips_whitespace():
    with patch(
        "app.tools.httpx.AsyncClient",
        return_value=_make_weather_mock("  London: ⛅ +15°C  \n"),
    ):
        result = await get_weather("london")
    assert not result.startswith(" ")
    assert not result.endswith((" ", "\n"))


# --- get_current_time ---


def test_get_current_time_format():
    result = get_current_time()
    # Expected format: YYYY-MM-DD HH:MM:SS
    from datetime import datetime

    datetime.strptime(result, "%Y-%m-%d %H:%M:%S")


def test_get_current_time_uses_now():
    with patch("app.tools.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.return_value = "2026-01-01 12:00:00"
        result = get_current_time()
    assert result == "2026-01-01 12:00:00"


# --- convert_temperature ---


def test_convert_temperature_freezing():
    assert convert_temperature(0) == "0°C is 32.0°F"


def test_convert_temperature_boiling():
    assert convert_temperature(100) == "100°C is 212.0°F"


def test_convert_temperature_body():
    assert convert_temperature(37) == "37°C is 98.6°F"


def test_convert_temperature_negative():
    assert convert_temperature(-40) == "-40°C is -40.0°F"


# --- roll_dice ---


def test_roll_dice_default_single():
    with patch("app.tools.random.randint", return_value=4):
        result = roll_dice()
    assert "1d6" in result
    assert "[4]" in result
    assert "total: 4" in result


def test_roll_dice_multiple():
    with patch("app.tools.random.randint", return_value=3):
        result = roll_dice(sides=8, count=3)
    assert "3d8" in result
    assert "total: 9" in result


def test_roll_dice_range():
    with patch("app.tools.random.randint", return_value=20):
        result = roll_dice(sides=20, count=1)
    assert "20" in result


# --- get_stock_price ---


def test_get_stock_price_known_symbol():
    with patch("app.tools.random.uniform", return_value=1.0):
        result = get_stock_price("AAPL")
    assert "AAPL" in result
    assert "$189.0" in result
    assert "+0.0" in result


def test_get_stock_price_unknown_symbol():
    with patch("app.tools.random.uniform", return_value=1.0):
        result = get_stock_price("XYZ")
    assert "XYZ" in result
    assert "$100.0" in result


def test_get_stock_price_lowercase_normalized():
    with patch("app.tools.random.uniform", return_value=1.0):
        result = get_stock_price("msft")
    assert "MSFT" in result


def test_get_stock_price_shows_negative_change():
    with patch("app.tools.random.uniform", return_value=0.95):
        result = get_stock_price("TSLA")
    assert "-" in result


# --- flip_coin ---


def test_flip_coin_heads():
    with patch("app.tools.random.choice", return_value="Heads"):
        result = flip_coin(count=3)
    assert "Heads: 3" in result
    assert "Tails: 0" in result


def test_flip_coin_tails():
    with patch("app.tools.random.choice", return_value="Tails"):
        result = flip_coin(count=2)
    assert "Tails: 2" in result
    assert "Heads: 0" in result


def test_flip_coin_default_count():
    with patch("app.tools.random.choice", return_value="Heads"):
        result = flip_coin()
    assert "Heads" in result


# --- get_fun_fact ---


def test_get_fun_fact_known_topics():
    for topic in ("space", "animals", "food", "math", "history", "general"):
        result = get_fun_fact(topic)
        assert isinstance(result, str)
        assert len(result) > 0


def test_get_fun_fact_unknown_topic_returns_general():
    general = get_fun_fact("general")
    unknown = get_fun_fact("unknowntopic")
    assert unknown == general


def test_get_fun_fact_case_insensitive():
    assert get_fun_fact("Space") == get_fun_fact("space")


# --- calculate_tip ---


def test_calculate_tip_default():
    result = calculate_tip(100.0)
    assert "$100.00" in result
    assert "$18.00" in result
    assert "$118.00" in result


def test_calculate_tip_custom_percent():
    result = calculate_tip(50.0, tip_percent=20.0)
    assert "$10.00" in result
    assert "$60.00" in result


def test_calculate_tip_split():
    result = calculate_tip(100.0, tip_percent=20.0, people=4)
    assert "Per person (4)" in result
    assert "$30.00" in result


def test_calculate_tip_no_split_hides_per_person():
    result = calculate_tip(100.0, people=1)
    assert "Per person" not in result
