-- Migration 0012: Add Oura OAuth tables
-- Date: 2024-01-XX

-- Create Oura user table
CREATE TABLE IF NOT EXISTS oura_user (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_sync DATETIME
);

-- Create Oura token table
CREATE TABLE IF NOT EXISTS oura_token (
    user_id TEXT PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    scope TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES oura_user(user_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_oura_user_email ON oura_user(email);
CREATE INDEX IF NOT EXISTS idx_oura_token_expires ON oura_token(expires_at);
