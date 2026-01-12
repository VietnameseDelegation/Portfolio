# Test Cases

This document outlines manual test scenarios to verify the functionality of the DatabaseProject.

## 1. ETL Process Testing

### 1.1 Import Data from CSV
**Description**: Verify that data from CSV files in the `input` folder is correctly loaded into the SQL Server database.
**Pre-conditions**:
-   `config.ini` is configured with valid DB credentials.
-   `input/` folder contains valid CSV files corresponding to tables (e.g., `users.csv`, `products.csv`).
-   Database tables are empty or ready for new data.
**Steps**:
1.  Open terminal in the project root.
2.  Run: `python main.py --import`
**Expected Result**:
-   Script completes without errors.
-   Console output shows processing time.
-   Verify in SQL Server: `SELECT COUNT(*) FROM users` (and other tables) returns the expected number of rows.

### 1.2 Export Data to CSV
**Description**: Verify that data can be exported from the database to CSV files.
**Pre-conditions**:
-   Database contains data.
**Steps**:
1.  Run: `python main.py --export`
2.  (Optional) Export specific table: `python main.py --export users`
**Expected Result**:
-   `export/` folder contains `users.csv` (and others).
-   File content matches database records.

## 2. API Endpoint Testing

### 2.1 Health Check / Root
**Description**: Verify API is running.
**Steps**:
1.  Start Backend: `python -m uvicorn api.main:app --reload`
2.  Navigate to `http://localhost:8000/` or curl it.
**Expected Result**:
-   JSON response: `{"message": "OrderSystem API is running"}`

### 2.2 User Management (via Swagger UI)
**Description**: Verify User CRUD operations.
**Steps**:
1.  Navigate to `http://localhost:8000/docs`.
2.  Expand **Users** section.
3.  Execute **GET /api/users/**.
**Expected Result**:
-   Response Code: 200 OK.
-   Response Body: List of user objects.

### 2.3 Product Listing
**Description**: Verify Products can be retrieved.
**Steps**:
1.  Expand **Products** section in Swagger (`/docs`).
2.  Execute **GET /api/products/**.
**Expected Result**:
-   Response Code: 200 OK.
-   List of product items.

## 3. Frontend Testing

### 3.1 Operations Dashboard
**Description**: Verify the main dashboard loads and communicates with the API.
**Pre-conditions**:
-   Backend is running (`localhost:8000`).
-   Frontend is running (`npm run dev`).
**Steps**:
1.  Open browser to `http://localhost:5173`.
2.  Verify home page loads.
3.  Navigate to **Users** or **Products** view (depending on UI layout).
**Expected Result**:
-   Data loading spinners appear and disappear.
-   Real data from the local database is displayed in tables/lists.
-   No "Network Error" alerts.

### 3.2 Data Entry (New Product)
**Description**: Verify form submission for creating a new product.
**Steps**:
1.  Navigate to **Products** -> **Add New**.
2.  Fill in valid product details.
3.  Submit form.
**Expected Result**:
-   Success notification appears.
-   New product appears in the list (possibly after refresh).
-   Verify in DB: `SELECT * FROM products WHERE name = '...'` exists.
