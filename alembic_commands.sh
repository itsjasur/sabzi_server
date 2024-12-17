
# If you want to reset the entire migration history
rm -rf alembic/versions/*

# Create a fresh migration based on current models
alembic revision --autogenerate -m "reset migrations"


# Apply the migration
alembic upgrade head

# If you have existing data and want to mark current state without migrations
alembic stamp head

# To fix a broken history when you have missing migrations
# First, get current database version
alembic current

# Then stamp the database with the known good version
alembic stamp <revision_id>

# Generate new migration from current state
alembic revision --autogenerate -m "migration_name"

# Verify migrations
alembic history
alembic check