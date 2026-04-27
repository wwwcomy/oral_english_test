-- oral_english_test SQLite schema
-- Notes:
-- - UUIDs stored as TEXT
-- - Timestamps stored as ISO-8601 TEXT (UTC recommended)
-- - JSON stored as TEXT

PRAGMA journal_mode = DELETE;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  owner_user_id TEXT,
  summary TEXT,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  last_message_time TEXT,
  last_sequence INTEGER NOT NULL DEFAULT 0,
  message_count INTEGER NOT NULL DEFAULT 0,
  create_time TEXT NOT NULL,
  updated_time TEXT NOT NULL,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  agent_name TEXT,
  sequence INTEGER NOT NULL,
  content TEXT NOT NULL,
  metadata TEXT,
  create_time TEXT NOT NULL,
  update_time TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_session_time ON messages(session_id, create_time);
CREATE INDEX IF NOT EXISTS idx_messages_session_seq ON messages(session_id, sequence);
