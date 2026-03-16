# 🧠 Neural BI Synthesis API

A secure, enterprise-grade **FastAPI** backend for Conversational Business Intelligence.  
Upload CSV/Excel datasets, ask natural language questions, and get back data insights + visualization metadata — all protected by JWT authentication.

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── auth.py          # Register & Login endpoints
│   │   └── endpoints.py     # Upload, Query, Datasets, History, Me
│   ├── core/
│   │   ├── agent.py         # BI AI agent (data analysis engine)
│   │   ├── auth.py          # JWT token validator / get_current_user
│   │   └── security.py      # Password hashing & JWT creation
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models (User, DataSnapshot, QueryLog)
│   │   └── session.py       # DB engine & session factory
│   └── utils/
│       └── helpers.py       # JSON serialization helpers
├── uploads/                 # Uploaded dataset files (per user)
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── run.py                   # Server launcher
```

---

## ⚙️ Tech Stack

| Layer        | Technology                                     |
|--------------|------------------------------------------------|
| Framework    | FastAPI 0.135                                  |
| Database     | PostgreSQL 16 (Primary) / SQLite (Fallback)    |
| Auth         | JWT (python-jose) + passlib                    |
| Data         | Pandas, NumPy                                  |
| AI/LLM       | OpenAI API                                     |
| Server       | Uvicorn                                        |

---

## 🚀 Setup — Step by Step

### Step 1 — Prerequisites

- Python 3.11+
- PostgreSQL 16 (Optional, but recommended for production)
- Git

### Step 2 — Clone & create virtual environment

```powershell
git clone <your-repo-url>
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1
```
#### Create and activate a virtual environment:
  - **For PowerShell**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
  - **For Run venv**:
    ```bash
    source venv/Scripts/activate
    ``` 

  - **For Git Bash / MINGW64**:
    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```
  - **For Run venv**:
    ```bash
    source venv/Scripts/activate
    ```  

### Step 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Create PostgreSQL database

Open **psql** or pgAdmin and run:

```sql
CREATE DATABASE agentic_bi;
```

### Step 5 — Configure `.env`

Edit the `.env` file in the backend root:

```env
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/agentic_bi

# JWT Secret (change this in production!)
SECRET_KEY=7b6d1e4f9b2c5a8e3d0f1a4c7b9e2d0f

# Optional: OpenAI API Key for advanced query synthesis
OPENAI_API_KEY=sk-...

PORT=8000
```

### Step 6 — Start the server

```powershell
# Option A — using run.py
python run.py

# Option B — using uvicorn directly
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Server will start at: **http://127.0.0.1:8000**  
Swagger API Docs: **http://127.0.0.1:8000/docs**

> **SQLite Fallback**: If you don't have PostgreSQL installed or haven't configured the `DATABASE_URL`, the system will automatically create a local `app.db` file in the backend root.

---

## 🗄️ Database & Migrations

### Automatic Migration
This project uses a **Startup Auto-Migration** strategy. 
- When the server starts (`python run.py`), SQLAlchemy checks for existing tables and creates any missing ones.
- **No Manual Command Needed**: You don't need to run `alembic upgrade head`.

### PostgreSQL vs SQLite
The backend is designed to be "plug-and-play":
1. **PostgreSQL**: Used if `DATABASE_URL` is set in `.env` and the service is reachable.
2. **SQLite**: Automatically used as a fallback if PostgreSQL is unavailable. This is ideal for local development.

### Resetting the Database
To perform a "hard reset" of your data:
- **SQLite**: Delete the `app.db` file and restart the server.
- **PostgreSQL**: Drop and recreate the database:
  ```sql
  DROP DATABASE agentic_bi;
  CREATE DATABASE agentic_bi;
  ```

---

## 🔐 Authentication

All endpoints (except `/register` and `/login`) require a **Bearer JWT token**.

The flow:
```
Register → Login → Get Token → Use Token in Authorization header
```

### Register

**POST** `/api/auth/register`

```json
// Request Body (JSON)
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "mypassword123"
}
```

```json
// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-03-15T07:00:00"
  }
}
```

---

### Login

**POST** `/api/auth/login`

> ⚠️ Login uses **form-data** (OAuth2 standard), NOT JSON.

```powershell
# curl example
curl -X POST http://127.0.0.1:8000/api/auth/login `
  -F "username=john@example.com" `
  -F "password=mypassword123"
```

```json
// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-03-15T07:00:00"
  }
}
```

> **In Swagger UI (`/docs`):** Click **Authorize 🔒** → enter email as `username` + password → Authorize.

---

## 📊 API Endpoints

All endpoints below require:
```
Authorization: Bearer <your_access_token>
```

---

### GET `/api/me` — Get Current User

```powershell
curl -X GET http://127.0.0.1:8000/api/me `
  -H "Authorization: Bearer <token>"
```

```json
// Response
{
  "id": 1,
  "username": "john@example.com",
  "full_name": "John Doe",
  "email": "john@example.com"
}
```

---

### POST `/api/upload` — Upload Dataset

Accepts `.csv`, `.xls`, `.xlsx` files.

```powershell
curl -X POST http://127.0.0.1:8000/api/upload `
  -H "Authorization: Bearer <token>" `
  -F "file=@sales_data.csv"
```

```json
// Response
{
  "filename": "sales_data.csv",
  "columns": ["Date", "Product", "Category", "Sales", "Profit"],
  "rows": 1500,
  "sample": [
    { "Date": "2024-01-01", "Product": "Widget A", "Sales": 1200 },
    ...
  ]
}
```

---

### POST `/api/query` — Natural Language Query

Ask any question about your uploaded dataset.

```powershell
curl -X POST "http://127.0.0.1:8000/api/query?query=show+me+sales+by+category&file_id=sales_data.csv" `
  -H "Authorization: Bearer <token>"
```

```json
// Response
{
  "answer": "Analysis of Sales by Category.",
  "viz": "bar",
  "data": [
    { "Category": "Electronics", "Sales": 45000 },
    { "Category": "Clothing",    "Sales": 28000 },
    { "Category": "Food",        "Sales": 17000 }
  ],
  "metadata": { "x": "Category", "y": "Sales" }
}
```

**Supported query keywords:**

| Keyword(s)                          | Visualization |
|-------------------------------------|---------------|
| `pie`, `ratio`, `breakdown`         | 🥧 Pie chart  |
| `trend`, `line`, `over time`        | 📈 Line chart |
| `area`                              | 🏔️ Area chart |
| `scatter`, `correlation`            | ⬛ Scatter    |
| `list`, `table`, `raw`              | 📋 Table      |
| `kpi`, `summary`, `dashboard`       | 📊 Dashboard  |
| *(default)*                         | 📊 Bar chart  |

---

### GET `/api/datasets` — List All Datasets

```powershell
curl -X GET http://127.0.0.1:8000/api/datasets `
  -H "Authorization: Bearer <token>"
```

```json
// Response
[
  {
    "id": 1,
    "filename": "sales_data.csv",
    "columns": "Date,Product,Category,Sales,Profit",
    "rows_count": 1500,
    "created_at": "2026-03-15T07:10:00",
    "user_id": 1
  }
]
```

---

### DELETE `/api/datasets/{filename}` — Delete Dataset

Deletes the file from disk, the database record, and the in-memory cache.

```powershell
curl -X DELETE "http://127.0.0.1:8000/api/datasets/sales_data.csv" `
  -H "Authorization: Bearer <token>"
```

```json
// Response
{
  "message": "Dataset and history deleted successfully"
}
```

---

### GET `/api/history` — Query History

Returns the last 50 queries made by the logged-in user.

```powershell
curl -X GET http://127.0.0.1:8000/api/history `
  -H "Authorization: Bearer <token>"
```

```json
// Response
[
  {
    "id": 5,
    "query": "show me sales by category",
    "response": "Analysis of Sales by Category.",
    "viz_type": "bar",
    "created_at": "2026-03-15T08:00:00",
    "user_id": 1
  }
]
```

---

## 🗄️ Database Models

### `users`
| Column           | Type     | Notes              |
|------------------|----------|--------------------|
| id               | Integer  | Primary Key        |
| username         | String   | Same as email      |
| full_name        | String   | Display name       |
| email            | String   | Unique             |
| hashed_password  | Text     | pbkdf2_sha256      |
| created_at       | DateTime | Auto set           |

### `data_snapshots`
| Column     | Type    | Notes                    |
|------------|---------|--------------------------|
| id         | Integer | Primary Key              |
| filename   | String  | Original filename        |
| file_path  | Text    | Physical path on disk    |
| columns    | Text    | Comma-separated col list |
| rows_count | Integer | Row count at upload time |
| user_id    | Integer | FK → users.id            |
| created_at | DateTime| Auto set                 |

### `query_logs`
| Column     | Type    | Notes               |
|------------|---------|---------------------|
| id         | Integer | Primary Key         |
| query      | String  | User's question     |
| response   | Text    | AI answer text      |
| viz_type   | String  | bar/pie/line/table  |
| user_id    | Integer | FK → users.id       |
| created_at | DateTime| Auto set            |

---

## 🔑 Environment Variables

| Variable        | Required | Description                          |
|-----------------|----------|--------------------------------------|
| `DATABASE_URL`  | ✅       | PostgreSQL connection string         |
| `SECRET_KEY`    | ✅       | JWT signing secret                   |
| `OPENAI_API_KEY`| ❌       | For AI-powered query enhancement     |
| `PORT`          | ❌       | Server port (default: 8000)          |

---

## 🛠️ Common Issues & Fixes

| Error | Fix |
|-------|-----|
| `No module named 'email_validator'` | `pip install email-validator` |
| `No module named 'jose'` | `pip install python-jose[cryptography]` |
| `DATABASE_URL must be set` | Check your `.env` file exists and is loaded |
| `could not connect to server` | Make sure PostgreSQL service is running |
| `401 Unauthorized` on login | Use email as `username` field (not display name) |
| `422 Unprocessable Entity` on login | Login requires `form-data`, NOT JSON |

---

## 📦 Dependencies

```
fastapi          — Web framework
uvicorn          — ASGI server
sqlalchemy       — ORM
psycopg2         — PostgreSQL driver
python-jose      — JWT tokens
passlib          — Password hashing (pbkdf2_sha256)
pydantic         — Data validation
email-validator  — EmailStr support
pandas           — Data processing
python-dotenv    — .env loader
python-multipart — File upload support
openai           — AI query synthesis
```

---

## 🚦 Quick Test Flow

```powershell
# 1. Start server
python run.py

# 2. Register
curl -X POST http://127.0.0.1:8000/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"full_name":"Test User","email":"test@example.com","password":"pass123"}'

# 3. Login — save your token
curl -X POST http://127.0.0.1:8000/api/auth/login `
  -F "username=test@example.com" -F "password=pass123"

# 4. Upload a CSV
curl -X POST http://127.0.0.1:8000/api/upload `
  -H "Authorization: Bearer <TOKEN>" `
  -F "file=@your_data.csv"

# 5. Ask a question
curl -X POST "http://127.0.0.1:8000/api/query?query=show+total+sales+by+category&file_id=your_data.csv" `
  -H "Authorization: Bearer <TOKEN>"
```
