-- SQL script to fix user table schema
-- Run this against your PostgreSQL database

-- Add username column (nullable first, to allow existing rows)
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);

-- Add updated_at column
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Rename hashed_password to password_hash (if it exists)
DO $$
BEGIN
    IF EXISTS(SELECT 1 FROM information_schema.columns
             WHERE table_name='users' AND column_name='hashed_password') THEN
        ALTER TABLE users RENAME COLUMN hashed_password TO password_hash;
    END IF;
END $$;

-- Rename is_superuser to is_admin (if it exists)
DO $$
BEGIN
    IF EXISTS(SELECT 1 FROM information_schema.columns
             WHERE table_name='users' AND column_name='is_superuser') THEN
        ALTER TABLE users RENAME COLUMN is_superuser TO is_admin;
    END IF;
END $$;

-- Create unique constraint on username
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_username') THEN
        ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
    END IF;
END $$;

-- Create index on username
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);

-- Verify the changes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
