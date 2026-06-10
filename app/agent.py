import os

from strands import Agent
from strands.models.openai import OpenAIModel

from app.session.postgres_session_manager import PostgresSessionManager
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


def build_agent(session_id: str) -> Agent:
    model = OpenAIModel(
        client_args={"api_key": os.environ["OPENAI_API_KEY"]},
        model_id="gpt-4o-mini",
    )

    session_manager = PostgresSessionManager(
        session_id=session_id,
        connection_string=os.environ["DATABASE_URL"],
    )

    return Agent(
        model=model,
        tools=[
            get_weather,
            get_current_time,
            convert_temperature,
            roll_dice,
            get_stock_price,
            flip_coin,
            get_fun_fact,
            calculate_tip,
        ],
        session_manager=session_manager,
    )
