
CREATE DATABASE OrderSystem;
GO

USE OrderSystem;
GO


/* USERS */
CREATE TABLE users (
    id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) UNIQUE NOT NULL,
    registered_at DATETIME DEFAULT GETDATE()
);

/* CATEGORIES */
CREATE TABLE categories (
    id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) NOT NULL
);

/* PRODUCTS */
CREATE TABLE products (
    id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    price FLOAT NOT NULL,
    category_id INT,
    active BIT DEFAULT 1,
    CONSTRAINT FK_products_categories
        FOREIGN KEY (category_id) REFERENCES categories(id)
);

/* ORDERS */
CREATE TABLE orders (
    id INT IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME DEFAULT GETDATE(),
    status NVARCHAR(20) NOT NULL,
    paid BIT DEFAULT 0,

    CONSTRAINT FK_orders_users
        FOREIGN KEY (user_id) REFERENCES users(id),

    CONSTRAINT CHK_order_status
        CHECK (status IN ('new', 'paid', 'shipped', 'cancelled'))
);

/* ORDER_ITEMS (M:N) */
CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_order FLOAT NOT NULL,

    CONSTRAINT PK_order_items
        PRIMARY KEY (order_id, product_id),

    CONSTRAINT FK_order_items_orders
        FOREIGN KEY (order_id) REFERENCES orders(id),

    CONSTRAINT FK_order_items_products
        FOREIGN KEY (product_id) REFERENCES products(id)
);

/* PAYMENTS */
CREATE TABLE payments (
    id INT IDENTITY PRIMARY KEY,
    order_id INT NOT NULL,
    amount FLOAT NOT NULL,
    payment_date DATETIME DEFAULT GETDATE(),
    method NVARCHAR(20) NOT NULL,

    CONSTRAINT FK_payments_orders
        FOREIGN KEY (order_id) REFERENCES orders(id),

    CONSTRAINT CHK_payment_method
        CHECK (method IN ('card', 'cash', 'bank_transfer'))
);
go



/* VIEW 1 – Order summary */
CREATE VIEW view_order_summary AS
SELECT
    o.id AS order_id,
    u.name AS customer_name,
    o.order_date,
    o.status,
    SUM(oi.quantity * oi.price_at_order) AS total_price
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, u.name, o.order_date, o.status;
GO

/* VIEW 2 – Product sales */
CREATE VIEW view_product_sales AS
SELECT
    p.name AS product_name,
    SUM(oi.quantity) AS total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.name;
GO

