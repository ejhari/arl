"""
Direct database schema fix using asyncpg directly with connection from .env
"""
import asyncio
import asyncpg
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

async def fix_schema():
    """Apply schema fixes directly"""
    # Extract connection parameters from DATABASE_URL
    db_url = settings.DATABASE_URL

    print(f"Connecting to database...")
    print(f"Database URL pattern: {db_url.split('@')[1] if '@' in db_url else 'unknown'}")

    try:
        # Parse the DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        parts = db_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')

        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        database = host_db[1] if len(host_db) > 1 else 'postgres'

        print(f"Connecting as user '{user}' to database '{database}' on {host}:{port}")

        # Connect directly with asyncpg
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        print("\n✅ Connected successfully!")
        print("\nApplying schema fixes...\n")

        # 1. Add username column
        print("1. Adding username column...")
        await conn.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='username'
                ) THEN
                    ALTER TABLE users ADD COLUMN username VARCHAR(100);
                    RAISE NOTICE 'Added username column';
                ELSE
                    RAISE NOTICE 'username column already exists';
                END IF;
            END $$;
        """)

        # 2. Add updated_at column
        print("2. Adding updated_at column...")
        await conn.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='updated_at'
                ) THEN
                    ALTER TABLE users ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
                    RAISE NOTICE 'Added updated_at column';
                ELSE
                    RAISE NOTICE 'updated_at column already exists';
                END IF;
            END $$;
        """)

        # 3. Rename hashed_password to password_hash
        print("3. Renaming hashed_password to password_hash...")
        await conn.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='hashed_password'
                ) THEN
                    ALTER TABLE users RENAME COLUMN hashed_password TO password_hash;
                    RAISE NOTICE 'Renamed hashed_password to password_hash';
                ELSE
                    RAISE NOTICE 'Column already renamed or does not exist';
                END IF;
            END $$;
        """)

        # 4. Rename is_superuser to is_admin
        print("4. Renaming is_superuser to is_admin...")
        await conn.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='is_superuser'
                ) THEN
                    ALTER TABLE users RENAME COLUMN is_superuser TO is_admin;
                    RAISE NOTICE 'Renamed is_superuser to is_admin';
                ELSE
                    RAISE NOTICE 'Column already renamed or does not exist';
                END IF;
            END $$;
        """)

        # 5. Add unique constraint on username
        print("5. Adding unique constraint on username...")
        await conn.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_username'
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
                    RAISE NOTICE 'Added unique constraint on username';
                ELSE
                    RAISE NOTICE 'Unique constraint already exists';
                END IF;
            END $$;
        """)

        # 6. Create index on username
        print("6. Creating index on username...")
        await conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
        """)

        # 7. Verify the schema
        print("\n" + "="*60)
        print("VERIFICATION: Current users table schema")
        print("="*60)

        rows = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)

        for row in rows:
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {row['column_default']}" if row['column_default'] else ""
            print(f"  {row['column_name']:20} {row['data_type']:20} {nullable}{default}")

        print("\n✅ Schema fix completed successfully!")
        print("\n⚠️  NOTE: Existing users will have NULL usernames.")
        print("   You'll need to update them before making username NOT NULL.\n")

        await conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_schema())
