"""add profiles table

Revision ID: c9a8f7e4d2b1
Revises: b32298f31227
Create Date: 2026-01-22 19:51:00.000000

"""

from typing import Sequence, Union

from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9a8f7e4d2b1"
down_revision: Union[str, Sequence[str], None] = "b32298f31227"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Note: This migration is idempotent and safe to run even if the table
    already exists in Supabase (created via SQL script). It serves as
    version control and documentation of the schema.

    For test environments where auth schema doesn't exist, creates table
    without foreign key constraint.
    """
    # Create user_role enum type
    user_role_enum = postgresql.ENUM("ADMIN", "MEMBER", name="user_role", create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Check if auth schema exists (Supabase only)
    connection = op.get_bind()
    result = connection.execute(
        text("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth')")
    )
    auth_schema_exists = result.scalar()

    # Create profiles table with conditional foreign key
    if auth_schema_exists:
        op.execute("""
            CREATE TABLE IF NOT EXISTS public.profiles (
                id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
                email TEXT NOT NULL,
                role user_role NOT NULL DEFAULT 'MEMBER',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    else:
        # Test environment: no foreign key constraint
        op.execute("""
            CREATE TABLE IF NOT EXISTS public.profiles (
                id UUID NOT NULL PRIMARY KEY,
                email TEXT NOT NULL,
                role user_role NOT NULL DEFAULT 'MEMBER',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

    # RLS policies and triggers only for Supabase (when auth schema exists)
    if auth_schema_exists:
        # Enable RLS
        op.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY")

        # Create RLS policies (drop first if exists to be idempotent)
        op.execute("""
            DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON profiles
        """)
        op.execute("""
            CREATE POLICY "Public profiles are viewable by everyone"
            ON profiles FOR SELECT
            USING (true)
        """)

        op.execute("""
            DROP POLICY IF EXISTS "Users can update their own profile" ON profiles
        """)
        op.execute("""
            CREATE POLICY "Users can update their own profile"
            ON profiles FOR UPDATE
            USING (auth.uid() = id)
        """)

        # Create trigger function
        op.execute("""
            CREATE OR REPLACE FUNCTION public.handle_new_user()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            SECURITY DEFINER SET search_path = public
            AS $$
            BEGIN
                INSERT INTO public.profiles (id, email, role)
                VALUES (new.id, new.email, 'MEMBER');
                RETURN new;
            END;
            $$
        """)

        # Create trigger
        op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users")
        op.execute("""
            CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user()
        """)


def downgrade() -> None:
    """Downgrade schema."""
    # Check if auth schema exists (Supabase only)
    connection = op.get_bind()
    result = connection.execute(
        text("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth')")
    )
    auth_schema_exists = result.scalar()

    # Only drop auth-related objects if auth schema exists
    if auth_schema_exists:
        # Drop trigger
        op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users")

        # Drop trigger function
        op.execute("DROP FUNCTION IF EXISTS public.handle_new_user()")

        # Drop RLS policies
        op.execute("""
            DROP POLICY IF EXISTS "Users can update their own profile" ON profiles
        """)
        op.execute("""
            DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON profiles
        """)

    # Drop table (safe for both environments)
    op.execute("DROP TABLE IF EXISTS public.profiles")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS user_role")
