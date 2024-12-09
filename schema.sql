-- Create the users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- Unique user ID
    username VARCHAR(50) NOT NULL UNIQUE,     -- Username (must be unique)
    email VARCHAR(100) NOT NULL UNIQUE,       -- Email (must be unique)
    password VARCHAR(255) NOT NULL,           -- Hashed password
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of registration
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- Timestamp of last update
);

-- Optionally, create an index on email for faster lookup
CREATE INDEX idx_email ON users (email);
