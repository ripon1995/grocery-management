# Repo structure

````
backend/
├── .python-version
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── router.py
│   ├── common/
│   │   ├── enums.py
│   │   ├── filters.py
│   │   ├── pagination.py
│   │   └── responses.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── features/
│   │   └── grocery/
│   │       ├── __init__.py
│   │       ├── dependencies.py
│   │       ├── models.py
│   │       ├── repository.py
│   │       ├── router.py
│   │       ├── schemas/
│   │       │   ├── grocery_base.py
│   │       │   ├── request_schemas.py
│   │       │   └── response_schemas.py
│   │       └── service.py
│   ├── main.py
│   └── utils/
│       ├── constants.py
│       └── enums.py
├── migrations/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── README.md
└── requirements.txt

````