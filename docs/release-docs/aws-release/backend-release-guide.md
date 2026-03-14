# Grocery Management Backend – Setup on Ubuntu (AWS EC2 / similar VPS)

Last tested: March 2025  
Environment: Fresh Ubuntu (likely 22.04 / 24.04) on cloud instance

## Goal

Run a FastAPI (or similar) backend project located at:

in the `backend/` folder using:

- Python virtual environment
- Uvicorn + FastAPI
- Alembic for migrations
- `.env` file for configuration

## Final Working Steps (Clean Version – Recommended)

```bash
# 1. Update system & install basics
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv

# 2. Clone the project (if not already done)
git clone https://github.com/ripon1995/grocery-management.git
cd grocery-management/backend

# 3. Create and activate virtual environment (in backend directory)
python3 -m venv .venv
source .venv/bin/activate

# You should now see (.venv) in your prompt

# 4. Upgrade pip inside venv
pip install --upgrade pip

# 5. Install project dependencies
# (make sure the file is really named requirements.txt – not requirement.txt)
pip install -r requirements.txt

# 6. Create .env file (very important!)
# Example minimal content – adjust values!
cat > .env << 'EOF'
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/grocery_db
SECRET_KEY=your-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# Add any other required variables from config.py
EOF

# 7. Check/alter config if needed (sometimes hard-coded values are there)
# vim app/core/config.py

# 8. Run database migrations (Alembic)
alembic upgrade head

# Common error fixes:
# • alembic not found   →  pip install alembic
# • No database → make sure PostgreSQL is running + correct DATABASE_URL

# 9. Start the FastAPI server (accessible from outside)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Recommended production flags (without --reload):
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4


# Final step to run the service in detouch mode using nohup(instead of 9) 
# Recommended (redirects output to file so you can see logs later)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > uvicorn.log 2>&1 &
# Or minimal version (logs go to nohup.out by default)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &