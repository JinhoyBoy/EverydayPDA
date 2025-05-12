-- Create users table
CREATE TABLE users (
    u_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    course VARCHAR(100),
    cafeteria VARCHAR(100),
    city VARCHAR(100),
    preferred_transport_medium VARCHAR(100)
);

-- Create stocks table
CREATE TABLE stocks (
    s_id SERIAL PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL
);

-- Create news table
CREATE TABLE news (
    n_id SERIAL PRIMARY KEY,
    news_name VARCHAR(255) NOT NULL
);

-- Create user-stock relationship table with ON DELETE CASCADE
CREATE TABLE user_stocks (
    id SERIAL PRIMARY KEY,
    u_id INT,
    s_id INT,
    FOREIGN KEY (u_id) REFERENCES users(u_id) ON DELETE CASCADE,
    FOREIGN KEY (s_id) REFERENCES stocks(s_id) ON DELETE CASCADE
);

-- Create user-news relationship table with ON DELETE CASCADE
CREATE TABLE user_news (
    id SERIAL PRIMARY KEY,
    u_id INT,
    n_id INT,
    FOREIGN KEY (n_id) REFERENCES news(n_id) ON DELETE CASCADE
);
