"""PostgreSQL-backed session manager for Strands agents."""

import logging
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from strands.session.repository_session_manager import RepositorySessionManager
from strands.session.session_repository import SessionRepository
from strands.types.exceptions import SessionException
from strands.types.session import Session, SessionAgent, SessionMessage

logger = logging.getLogger(__name__)


class PostgresSessionManager(RepositorySessionManager, SessionRepository):
    """PostgreSQL-backed session manager."""

    def __init__(self, session_id: str, connection_string: str, **kwargs: Any):
        self._conn = psycopg.connect(connection_string)
        self._conn.autocommit = True
        super().__init__(session_id=session_id, session_repository=self, **kwargs)

    def create_session(self, session: Session, **kwargs: Any) -> Session:
        self._conn.execute(
            "INSERT INTO sessions (session_id, data) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            [session.session_id, Jsonb(session.to_dict())],
        )
        return session

    def read_session(self, session_id: str, **kwargs: Any) -> Session | None:
        row = self._conn.execute(
            "SELECT data FROM sessions WHERE session_id = %s",
            [session_id],
        ).fetchone()
        return Session.from_dict(row[0]) if row else None

    def create_agent(
        self, session_id: str, session_agent: SessionAgent, **kwargs: Any
    ) -> None:
        self._conn.execute(
            "INSERT INTO session_agents (session_id, agent_id, data) VALUES (%s, %s, %s)",
            [session_id, session_agent.agent_id, Jsonb(session_agent.to_dict())],
        )

    def read_agent(
        self, session_id: str, agent_id: str, **kwargs: Any
    ) -> SessionAgent | None:
        row = self._conn.execute(
            "SELECT data FROM session_agents WHERE session_id = %s AND agent_id = %s",
            [session_id, agent_id],
        ).fetchone()
        return SessionAgent.from_dict(row[0]) if row else None

    def update_agent(
        self, session_id: str, session_agent: SessionAgent, **kwargs: Any
    ) -> None:
        previous = self.read_agent(session_id, session_agent.agent_id)
        if previous is None:
            raise SessionException(
                f"Agent {session_agent.agent_id} in session {session_id} does not exist"
            )
        session_agent.created_at = previous.created_at
        self._conn.execute(
            "UPDATE session_agents SET data = %s, updated_at = now() WHERE session_id = %s AND agent_id = %s",
            [Jsonb(session_agent.to_dict()), session_id, session_agent.agent_id],
        )

    def create_message(
        self,
        session_id: str,
        agent_id: str,
        session_message: SessionMessage,
        **kwargs: Any,
    ) -> None:
        self._conn.execute(
            "INSERT INTO session_messages (session_id, agent_id, message_id, data) VALUES (%s, %s, %s, %s)",
            [
                session_id,
                agent_id,
                session_message.message_id,
                Jsonb(session_message.to_dict()),
            ],
        )

    def read_message(
        self, session_id: str, agent_id: str, message_id: int, **kwargs: Any
    ) -> SessionMessage | None:
        row = self._conn.execute(
            "SELECT data FROM session_messages WHERE session_id = %s AND agent_id = %s AND message_id = %s",
            [session_id, agent_id, message_id],
        ).fetchone()
        return SessionMessage.from_dict(row[0]) if row else None

    def update_message(
        self,
        session_id: str,
        agent_id: str,
        session_message: SessionMessage,
        **kwargs: Any,
    ) -> None:
        previous = self.read_message(session_id, agent_id, session_message.message_id)
        if previous is None:
            raise SessionException(
                f"Message {session_message.message_id} does not exist"
            )
        session_message.created_at = previous.created_at
        self._conn.execute(
            "UPDATE session_messages SET data = %s, updated_at = now() "
            "WHERE session_id = %s AND agent_id = %s AND message_id = %s",
            [
                Jsonb(session_message.to_dict()),
                session_id,
                agent_id,
                session_message.message_id,
            ],
        )

    def list_messages(
        self,
        session_id: str,
        agent_id: str,
        limit: int | None = None,
        offset: int = 0,
        **kwargs: Any,
    ) -> list[SessionMessage]:
        if limit is not None:
            rows = self._conn.execute(
                "SELECT data FROM session_messages WHERE session_id = %s AND agent_id = %s "
                "ORDER BY message_id LIMIT %s OFFSET %s",
                [session_id, agent_id, limit, offset],
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT data FROM session_messages WHERE session_id = %s AND agent_id = %s "
                "ORDER BY message_id OFFSET %s",
                [session_id, agent_id, offset],
            ).fetchall()
        return [SessionMessage.from_dict(row[0]) for row in rows]
