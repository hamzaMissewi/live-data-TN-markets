The backend has two issues:

1. **Port 8000 already in use** — the previous server instance (PID 25228) is still running.
2. **Database connection failed** — `.env` points to hostname `postgres` (Docker service name) instead of `localhost`.

Here's the fix:

### 1. Kill the existing process on port 8000

```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Or kill all Python processes:
```cmd
taskkill /F /IM python.exe
```

### 2. Fix the database URL in `.env`

Edit `backend/.env` — change `postgres:5432` to `localhost:5432`:

```ini
# Before (Docker service name - won't work without Docker):
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/tunisia_markets

# After (localhost - works without Docker):
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tunisia_markets
```

### 3. Start PostgreSQL

You need PostgreSQL running on `localhost:5432`. Since Docker isn't available:

- **Option A:** Install PostgreSQL natively on Windows from [postgresql.org](https://www.postgresql.org/download/windows/)
- **Option B:** Start Docker Desktop then `docker-compose up -d postgres redis`

Create the database:
```sql
CREATE DATABASE tunisia_markets;
```

### 4. Re-run the backend

```bash
cd "e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend"
.venv\Scripts\Activate.ps1
python main.py
```

### 5. Verify

```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","version":"1.0.0"}

curl http://localhost:8000/api/v1/sectors
# Will work once PostgreSQL is running with seed data
```

**Summary:** You don't need Docker or `manage.py`. You need PostgreSQL on `localhost:5432` and to fix the `.env` `DATABASE_URL`, then kill the old process and restart.