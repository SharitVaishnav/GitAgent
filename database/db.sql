-- Drop old tables and start fresh
DROP TABLE IF EXISTS chat_history CASCADE;

-- Create conversation table
CREATE TABLE IF NOT EXISTS conversation (
    conv_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_query TEXT NOT NULL,
    assistant_output JSONB NOT NULL
);

-- Create session_chat table
CREATE TABLE IF NOT EXISTS session_chat (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    history JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Add foreign key constraint (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_session_id'
    ) THEN
        ALTER TABLE conversation 
        ADD CONSTRAINT fk_session_id 
        FOREIGN KEY (session_id) REFERENCES session_chat(session_id) ON DELETE CASCADE;
    END IF;
END $$;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_conversation_session_id ON conversation(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation(timestamp);
CREATE INDEX IF NOT EXISTS idx_session_username ON session_chat(username);
