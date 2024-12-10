#!/bin/bash

# deploy.sh

# 1. Backup database

timestamp=$(date +%Y%m%d_%H%M%S)
cp sql_app.db "sql_app.db.backup-$timestamp"

# 2. Pull latest code

git pull origin main

# 3. Install/update dependencies

pip install -r requirements.txt

# 4. Run migrations

alembic upgrade head

# 5. Restart your FastAPI service

# If using systemd:

sudo systemctl restart your_fastapi_service

# Or if using PM2:

# pm2 restart your_fastapi_app
