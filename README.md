# 🛒 Monthly Grocery Helper

```markdown
A full-stack monorepo application designed to manage monthly groceries efficiently.

## 🏗 Project Structure

- **`/backend`**: FastAPI (Python 3.14.2)
- **`/frontend`**: React + TypeScript + SWC (Vite)
- **`databse`**: supabase (free tier)

---

## 🚀 Getting Started

### Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) (for Python version management)
- [fnm] (for Node version manager)
- [npm](https://www.npmjs.com/) or [pnpm](https://pnpm.io/)

```

---

### 🐍 Backend Setup

- Navigate to the backend:

```bash
   cd backend

```

- Ensure the correct Python version is active:

```bash
pyenv local 3.14.2

```

- Create and activate the virtual environment:

```bash
python -m venv .grocery-helper-venv
source .grocery-helper-venv/bin/activate

```

- Install dependencies:

```bash
pip install -r requirements.txt

```

- Run the server:

```bash
uvicorn main:app --reload

```

---

### ⚛️ Frontend Setup

- Navigate to the frontend:

```bash
cd frontend

```

- Ensure the correct Python version is active:

```bash
fnm local 25

```

- Install dependencies:

```bash
npm install

```

- Start the development server:

```bash
npm run dev

```

---

## 🛠 Tech Stack

* **Backend:** FastAPI, Pydantic, uvicorn
* **Frontend:** React, TypeScript, Vite, SWC
* **Version Management:** Pyenv (Python), fnm(Node)

---
