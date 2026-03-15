# Grocery Management Frontend – Setup on Ubuntu (AWS EC2 / similar VPS)

Run a React frontend project located at:

in the `frontend/` folder using:

- React
- Node
- Vite

# Final Working Steps

## 1. Update system & install basics

```bash
sudo apt update
sudo apt upgrade -y
```

## 2. Install node

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 24

# Verify the Node.js version:
node -v # Should print "v24.14.0".

# Verify npm version:
npm -v # Should print "11.9.0".

```

## 3. Clone the project (if not already done)

```bash
git clone https://github.com/ripon1995/grocery-management.git
```

## 4. Install project dependencies

```bash
# go to front end directory
cd frontend
# clean install dependencies
npm ci
```

## 5. Run

option - 1:

```bash
# will block terminal
npm run dev-public
```

option - 2:

```bash
# will not block terminal
nohup npm run dev-public > vite.log 2>&1 &
```

## 6. Stop the process ran using nohup

```bash
# get the process id from here
ps aux | grep vite
# kill the process id
kill <process_id>
```