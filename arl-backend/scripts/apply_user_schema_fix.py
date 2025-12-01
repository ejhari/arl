"""
Script to apply user schema fix directly to the database.
This adds the missing username and updated_at columns, and renames existing columns.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def apply_migration():
    """Apply the user schema migration"""
    async with engine.begin() as conn:
        print("Starting migration...")

        try:
            # Add username column (nullable first)
            print("1. Adding username column...")
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100)"
            ))

            # Add updated_at column
            print("2. Adding updated_at column...")
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ))

            # Rename hashed_password to password_hash (only if the old column exists)
            print("3. Renaming hashed_password to password_hash...")
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS(SELECT 1 FROM information_schema.columns
                             WHERE table_name='users' AND column_name='hashed_password') THEN
                        ALTER TABLE users RENAME COLUMN hashed_password TO password_hash;
                    END IF;
                END $$;
            """))

            # Rename is_superuser to is_admin (only if the old column exists)
            print("4. Renaming is_superuser to is_admin...")
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS(SELECT 1 FROM information_schema.columns
                             WHERE table_name='users' AND column_name='is_superuser') THEN
                        ALTER TABLE users RENAME COLUMN is_superuser TO is_admin;
                    END IF;
                END $$;
            """))

            # Create unique constraint and index on username
            print("5. Adding unique constraint and index on username...")
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_username') THEN
                        ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
                    END IF;
                END $$;
            """))

            await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
            """))

            print("\n✅ Migration completed successfully!")
            print("\nNote: Existing rows have NULL usernames. You'll need to update them before making the column NOT NULL.")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise


async def main():
    """Main function"""
    try:
        await apply_migration()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
