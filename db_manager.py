#!/usr/bin/env python3
"""
Database management script using Alembic for schema migrations
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def setup_initial_migration():
    """Set up initial migration for clean database"""
    print("🔧 Setting up initial database migration...")
    
    # Create initial migration
    if create_migration("Initial database schema"):
        print("🔧 Applying initial migration...")
        return apply_migrations()
    return False


def auto_migrate():
    """Automatically detect changes and create + apply migration"""
    print("🔧 Auto-detecting schema changes...")
    
    # Create a timestamp for unique migration name
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Try to create migration
    if create_migration(f"Auto migration {timestamp}"):
        print("🔧 Applying new migration...")
        return apply_migrations()
    else:
        print("✅ No schema changes detected - database is up to date")
        return True


def reset_database():
    """Reset database and recreate from scratch"""
    print("🔧 Resetting database and applying fresh migrations...")
    
    # Downgrade to base (empty database)
    print("📉 Downgrading to base...")
    downgrade_migrations("base")
    
    # Apply all migrations
    print("📈 Applying all migrations...")
    return apply_migrations()


def create_migration(message):
    """Create a new migration"""
    return run_command(
        f"uv run alembic revision --autogenerate -m \"{message}\"",
        f"Creating migration: {message}"
    )


def apply_migrations():
    """Apply all pending migrations"""
    return run_command(
        "uv run alembic upgrade head",
        "Applying migrations"
    )


def show_current_revision():
    """Show current database revision"""
    return run_command(
        "uv run alembic current",
        "Showing current revision"
    )


def show_migration_history():
    """Show migration history"""
    return run_command(
        "uv run alembic history",
        "Showing migration history"
    )


def downgrade_migrations(target="base"):
    """Downgrade migrations to target"""
    return run_command(
        f"uv run alembic downgrade {target}",
        f"Downgrading to {target}"
    )


def show_help():
    """Show help information"""
    print("""
🗃️  DATABASE MIGRATION MANAGER

Usage: python db_manager.py <command> [options]

Available commands:
  setup              Set up initial database schema (for fresh start)
  create <message>   Create a new migration with the given message
  migrate            Apply all pending migrations
  auto               Auto-detect changes and create + apply migration
  reset              Reset database and reapply all migrations
  current            Show current database revision
  history            Show migration history
  downgrade [target] Downgrade to target revision (default: base)
  help               Show this help message

Examples:
  python db_manager.py setup
  python db_manager.py create "Add new table"
  python db_manager.py migrate
  python db_manager.py auto
  python db_manager.py reset
  python db_manager.py current

🔧 Advanced Alembic commands:
  uv run alembic revision --autogenerate -m "message"
  uv run alembic upgrade head
  uv run alembic downgrade -1
  uv run alembic show <revision>
  uv run alembic stamp head
""")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "setup":
        setup_initial_migration()

    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Error: Migration message required")
            print("Usage: python db_manager.py create <message>")
            return
        message = " ".join(sys.argv[2:])
        create_migration(message)

    elif command == "migrate":
        apply_migrations()

    elif command == "auto":
        auto_migrate()

    elif command == "reset":
        reset_database()

    elif command == "current":
        show_current_revision()

    elif command == "history":
        show_migration_history()

    elif command == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "base"
        downgrade_migrations(target)

    elif command == "help":
        show_help()

    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    print("=" * 60)
    print("🗃️  MEDEX SCRAPER - DATABASE MIGRATION MANAGER")
    print("=" * 60)
    main()
