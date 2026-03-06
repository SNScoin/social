# Social Media Stats Dashboard

Multi-platform social media analytics tracker with Monday.com integration.

## Architecture

```
common/    → Shared constants, validators, error codes
backend/   → Node.js + Express API (port 3001)
frontend/  → Next.js 14 (port 3000)
parsers/   → Standalone social media parser package
legacy/    → Previous Python/React codebase (archived)
```

## Quick Start

### 1. Start databases
```bash
docker-compose up -d
```

### 2. Backend
```bash
cd backend
cp .env.example .env    # Edit with your API keys
npm install
npm run migrate         # Create database tables
npm run seed            # Add test user (admin@test.com / password123)
npm run dev             # Start on port 3001
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev             # Start on port 3000
```

### 4. Verify
- Frontend: http://localhost:3000
- Backend health: http://localhost:3001/api/v1/health
- Login: admin@test.com / password123

## Company Types

| Type | Links Source | Metrics Destination |
|---|---|---|
| **Manual** | User adds links manually | Dashboard only |
| **Monday.com** | Imported from Monday board column | Dashboard + Monday board columns |
