-- ASU1-Loom Database Initialization Script
-- PostgreSQL Database Setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database (if running manually)
-- CREATE DATABASE loom_db;

-- Connect to database
-- \c loom_db;

-- Create tables will be handled by SQLAlchemy migrations
-- This file is for any initial data or custom setup

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but listed here for reference

-- Containers table indexes:
-- CREATE INDEX IF NOT EXISTS idx_containers_name ON containers(name);
-- CREATE INDEX IF NOT EXISTS idx_containers_subdomain ON containers(subdomain);
-- CREATE INDEX IF NOT EXISTS idx_containers_status ON containers(status);
-- CREATE INDEX IF NOT EXISTS idx_containers_user_id ON containers(user_id);

-- Users table indexes:
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE loom_db TO loom_user;

-- Success message
SELECT 'ASU1-Loom database initialized successfully!' AS message;
