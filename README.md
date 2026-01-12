# DatabaseProject

A full-stack application with a Python FastAPI backend and a React (Vite) frontend, including an ETL processor for CSV to SQL Server data migration.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python** (3.10+ recommended)
2.  **Node.js** (LTS version recommended)
3.  **SQL Server** (with ODBC Driver 17 for SQL Server)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DatabaseProject
```

### 2. Backend Setup
Create a virtual environment and install dependencies:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Frontend Setup
Install Node.js dependencies:

```bash
# From the root directory (or inside /frontend)
cd frontend
npm install
cd ..
npm install # Install root dependencies (concurrently)
```

## Configuration

### Database Configuration
1.  Locate `config.ini` in the root directory.
2.  Update the `[DATABASE]` section with your SQL Server credentials:

```ini
[DATABASE]
server = YOUR_SERVER_NAME
database = OrderSystem
username = YOUR_USERNAME
password = YOUR_PASSWORD
driver = ODBC Driver 17 for SQL Server
trusted_connection = no
encrypt = no
```

> [!NOTE]
> If `config.ini` does not exist, run the ETL processor once to generate a default one, or copy the structure above.

### Database Schema
Initialize your database using the provided schema file:
1.  Open `schema.sql`.
2.  Execute the script in your SQL Server instance to create the necessary tables (`users`, `products`, `orders`, etc.).

## Running the Application

### Development Mode (Recommended)
You can run both the backend and frontend concurrently from the root directory:

```bash
npm run dev
```

This will start:
-   **Frontend**: http://localhost:5173
-   **Backend**: http://localhost:8000
-   **API Docs**: http://localhost:8000/docs

### Manual Start
If you prefer running them in separate terminals:

**Terminal 1 (Backend):**
```bash
.\venv\Scripts\activate
python -m uvicorn api.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## ETL Processor (CSV to SQL)
To import CSV data:

```bash
python main.py --import --config config.ini
```

To export tables to CSV:
```bash
python main.py --export --config config.ini
```
