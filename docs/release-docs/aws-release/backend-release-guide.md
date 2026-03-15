# Grocery Management Backend – Setup on Ubuntu (AWS EC2 / similar VPS)

Run a FastAPI (or similar) backend project located at:

in the `backend/` folder using:

- Python virtual environment
- uvicorn + FastAPI
- Alembic for migrations
- `.env` file for configuration

# Final Working Steps

## 1. Update system & install basics

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv
```

## 2. Clone the project (if not already done)

```bash
git clone https://github.com/ripon1995/grocery-management.git
```

## 3. Create and activate virtual environment (in backend directory)

```bash
cd grocery-management/backend
python3 -m venv .venv
source .venv/bin/activate
```

## You should now see (.venv) in your prompt

## 4. Upgrade pip inside venv

```bash
pip install --upgrade pip
```

## 5. Install project dependencies

```bash
pip install -r requirements.txt
```

## 6 Create .env file from the template (.env.sample):

```bash
cp .env.sample .env
```

## edit the file using vim

```bash
vim .env
```

## 7. Check/alter config if needed

```bash
cd app/core/config.py
vim config.py
```

## 8. Run database migrations (Alembic)

```bash
alembic upgrade head
```

## 9. Start the FastAPI server (accessible from outside)

Option - 1:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Recommended production flags (without --reload):

Option - 2:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Recommended (redirects output to file so you can see logs later)

Option - 3:

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > uvicorn.log 2>&1 &
```

# Or minimal version (logs go to nohup.out by default)

Option - 4

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &
```

## 10. Stop the process ran using nohup

```bash
# get the process id from here
ps aux | grep uvicorn
# kill the process id
kill <process_id>
```