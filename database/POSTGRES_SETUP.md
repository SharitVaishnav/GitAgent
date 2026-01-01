# PostgreSQL Setup for Chat History

## Prerequisites

You need PostgreSQL installed and running on your system.

### Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Or use Docker:**
```bash
docker run --name postgres-chat \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=chat_history \
  -p 5432:5432 \
  -d postgres:14
```

## Configuration

Update the `.env` file with your PostgreSQL credentials:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chat_history
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

## Install Python Dependencies

```bash
pip install psycopg2-binary
```

## Database Schema

The application will automatically create the following table on startup:

```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    username TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    user_query TEXT NOT NULL,
    agent_response TEXT NOT NULL
);

-- Indexes
CREATE INDEX idx_session_id ON chat_history(session_id);
CREATE INDEX idx_username ON chat_history(username);
CREATE INDEX idx_timestamp ON chat_history(timestamp);
```

## Verify Setup

After starting your server, check the logs for:
```
PostgreSQL database initialized: chat_history at localhost
```

## Querying the Database

You can connect to PostgreSQL and query the chat history:

```bash
psql -U postgres -d chat_history

# View all chat history
SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 10;

# View history for a specific user
SELECT * FROM chat_history WHERE username = 'YourGitHubUsername';

# View history for a specific session
SELECT * FROM chat_history WHERE session_id = 'your-session-id';
```
