CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    data       JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session_agents (
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    agent_id   TEXT NOT NULL,
    data       JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (session_id, agent_id)
);

CREATE TABLE IF NOT EXISTS session_messages (
    session_id TEXT    NOT NULL,
    agent_id   TEXT    NOT NULL,
    message_id INTEGER NOT NULL,
    data       JSONB   NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (session_id, agent_id, message_id),
    FOREIGN KEY (session_id, agent_id) REFERENCES session_agents(session_id, agent_id)
);
