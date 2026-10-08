"""
Dev DB bootstrap: wait for postgres -> run migrations (creates tables) -> seed random groceries.
Seeding is skipped when the grocery table already has rows, so it is safe to run on every startup.

Usage (from backend/):  python -m scripts.seed_groceries
Env:  SEED_GROCERY_COUNT (default 100000)
"""

import asyncio
import os
import random
import time
import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import func, insert, select, text

from app.common.enums import GroceryType, Seller, GroceryCategory
from app.db.session import engine
from app.features.grocery.models import Grocery

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"
SEED_COUNT = int(os.getenv("SEED_GROCERY_COUNT", "100000"))
BATCH_SIZE = 2_000
DB_WAIT_ATTEMPTS = 30

SELLERS = [s for s in Seller if s is not Seller.DEFAULT]

# category -> [(product, brands, type, sizes, (min_price, max_price))]
CATALOG: dict[GroceryCategory, list[tuple[str, list[str], GroceryType, list[str], tuple[int, int]]]] = {
    GroceryCategory.FOOD: [
        ("Miniket Rice", ["ACI", "Pran", "Teer", "Chashi", "Fresh"], GroceryType.SACK, ["5kg", "10kg", "25kg"], (400, 2_200)),
        ("Najirshail Rice", ["Shukran", "Chashi", "ACI", "Pran"], GroceryType.SACK, ["5kg", "10kg", "25kg"], (450, 2_400)),
        ("Atta", ["IFAD", "Teer", "Fresh", "Akij", "Pran"], GroceryType.PACKET, ["1kg", "2kg", "5kg"], (65, 330)),
        ("Masoor Dal", ["ACI", "Pran", "Teer", "Radhuni"], GroceryType.PACKET, ["500gm", "1kg", "2kg"], (70, 300)),
        ("Sugar", ["Fresh", "Teer", "ACI", "Deshbandhu"], GroceryType.PACKET, ["500gm", "1kg", "2kg"], (60, 280)),
        ("Salt", ["Teer", "ACI", "Molla", "Fresh"], GroceryType.PACKET, ["500gm", "1kg"], (20, 50)),
        ("Instant Noodles", ["Maggi", "Mr. Noodles", "Chopstick", "Cocola", "Ifad"], GroceryType.PACKET, ["4pcs", "8pcs", "12pcs", "16pcs"], (70, 380)),
        ("Full Cream Milk Powder", ["Diploma", "Marks", "Dano", "Fresh", "Nido"], GroceryType.PACKET, ["500gm", "1kg", "2.5kg"], (450, 2_400)),
        ("Rolled Oats", ["Kellogg's", "Quaker", "Saffola"], GroceryType.PACKET, ["500gm", "900gm", "1kg"], (300, 900)),
        ("Butter", ["Aarong", "Anchor", "Pran", "Milk Vita"], GroceryType.PIECE, ["100gm", "200gm", "400gm"], (120, 650)),
        ("Instant Coffee", ["Nescafe", "Davidoff", "Bru"], GroceryType.BOTTLE, ["50gm", "100gm", "200gm"], (250, 1_400)),
        ("Black Tea", ["Ispahani", "Seylon", "Tetley", "Finlay"], GroceryType.PACKET, ["200gm", "400gm", "500gm"], (120, 400)),
        ("Chicken Masala", ["Radhuni", "Pran", "BD Foods", "ACI Pure"], GroceryType.PACKET, ["20gm", "50gm", "100gm"], (25, 130)),
        ("Tomato Ketchup", ["Pran", "Ahmed", "Heinz", "Maggi"], GroceryType.BOTTLE, ["340gm", "500gm", "1kg"], (120, 450)),
        ("Mixed Fruit Jam", ["Pran", "Ahmed", "Fruitfun"], GroceryType.BOTTLE, ["350gm", "500gm"], (180, 350)),
        ("Canned Tuna", ["Ayam", "Sea Crown", "Golden Prize"], GroceryType.CAN, ["160gm", "185gm"], (220, 420)),
        ("Baked Beans", ["Heinz", "Ayam", "American Garden"], GroceryType.CAN, ["300gm", "415gm"], (180, 350)),
        ("Potato", ["Local Farm"], GroceryType.WEIGHT, ["1kg", "3kg", "5kg"], (40, 300)),
        ("Onion", ["Local Farm"], GroceryType.WEIGHT, ["1kg", "3kg", "5kg"], (60, 500)),
        ("Eggs", ["Kazi Farms", "Paragon", "CP"], GroceryType.PACKET, ["6pcs", "12pcs", "30pcs"], (80, 450)),
    ],
    GroceryCategory.OIL: [
        ("Soyabean Oil", ["Rupchanda", "Teer", "Fresh", "Pusti", "Bashundhara"], GroceryType.BOTTLE, ["1Ltr", "2Ltr", "5Ltr"], (180, 1_000)),
        ("Mustard Oil", ["Teer", "Radhuni", "Pran", "Rupchanda"], GroceryType.BOTTLE, ["250ml", "500ml", "1Ltr"], (90, 380)),
        ("Rice Bran Oil", ["Fresh", "Spondon", "Teer"], GroceryType.BOTTLE, ["1Ltr", "2Ltr", "5Ltr"], (220, 1_100)),
        ("Olive Oil", ["Borges", "Figaro", "Olitalia"], GroceryType.BOTTLE, ["250ml", "500ml", "1Ltr"], (450, 2_000)),
        ("Sunflower Oil", ["Fresh", "Bashundhara", "Teer"], GroceryType.BOTTLE, ["1Ltr", "2Ltr", "5Ltr"], (250, 1_300)),
    ],
    GroceryCategory.COOKIES: [
        ("Chanachur", ["Bombay Sweets", "Ruchi", "Pran", "BD Foods"], GroceryType.PACKET, ["150gm", "300gm", "500gm"], (50, 200)),
        ("Marie Biscuit", ["Olympic", "Pran", "Haque", "Bisk Club"], GroceryType.PACKET, ["100gm", "200gm", "300gm"], (25, 90)),
        ("Special Toast", ["Pran", "Olympic", "Haque", "Romania"], GroceryType.PACKET, ["150gm", "300gm"], (40, 120)),
        ("Chocolate Cookies", ["Oreo", "Haque", "Danish", "Olympic"], GroceryType.PACKET, ["100gm", "200gm", "400gm"], (40, 250)),
        ("Butter Cookies", ["Danish", "Kelsen", "Royal Dansk"], GroceryType.CAN, ["340gm", "454gm", "908gm"], (450, 1_800)),
        ("Potato Chips", ["Pringles", "Lays", "Sun Chips", "Mr. Twist"], GroceryType.CAN, ["40gm", "110gm", "165gm"], (30, 420)),
    ],
    GroceryCategory.TOILETRIES: [
        ("Toothpaste", ["Colgate", "Pepsodent", "Closeup", "Sensodyne", "Meril"], GroceryType.PIECE, ["45gm", "100gm", "120gm", "200gm"], (60, 380)),
        ("Beauty Soap", ["Lux", "Lifebuoy", "Dove", "Lily", "Meril"], GroceryType.PIECE, ["75gm", "100gm", "150gm"], (40, 160)),
        ("Laundry Soap", ["Wheel", "Rin", "Tibet"], GroceryType.PIECE, ["125gm", "130gm"], (25, 45)),
        ("Detergent Powder", ["Wheel", "Surf Excel", "Rin", "Jet", "Chaka"], GroceryType.PACKET, ["500gm", "1kg", "2kg"], (60, 600)),
        ("Liquid Detergent", ["Surf Excel", "Ariel", "Rin"], GroceryType.BOTTLE, ["500ml", "1Ltr", "2Ltr"], (180, 900)),
        ("Dishwash Bar", ["Vim", "Trix", "Chamak"], GroceryType.PIECE, ["100gm", "300gm"], (15, 60)),
        ("Dishwash Liquid", ["Vim", "Trix", "Pril"], GroceryType.BOTTLE, ["250ml", "500ml", "1Ltr"], (60, 300)),
        ("Surface Cleaner", ["Lizol", "Harpic", "Savlon"], GroceryType.BOTTLE, ["500ml", "1Ltr"], (150, 420)),
        ("Toilet Tissue", ["Fresh", "Bashundhara", "Kleenex"], GroceryType.PIECE, ["1 Roll", "4 Rolls", "12 Rolls"], (25, 400)),
        ("Hand Towel", ["Fresh", "Bashundhara", "Tissue Plus"], GroceryType.PACKET, ["25pcs", "100pcs", "250pcs"], (40, 180)),
        ("Shampoo", ["Sunsilk", "Head & Shoulders", "Pantene", "Clear", "Dove"], GroceryType.BOTTLE, ["180ml", "340ml", "650ml"], (220, 1_100)),
        ("Hand Wash", ["Lifebuoy", "Dettol", "Savlon"], GroceryType.BOTTLE, ["200ml", "250ml", "1Ltr"], (90, 380)),
    ],
    GroceryCategory.OTHER: [
        ("Batteries AA", ["Duracell", "Panasonic", "Energizer"], GroceryType.PACKET, ["2pcs", "4pcs"], (80, 400)),
        ("Aluminium Foil", ["Diamond", "Fresh Wrap", "Hotpack"], GroceryType.PIECE, ["10m", "25m"], (120, 450)),
        ("Garbage Bag", ["Hotpack", "Fresh", "RFL"], GroceryType.PACKET, ["15pcs", "30pcs"], (60, 220)),
        ("Mosquito Coil", ["Good Knight", "ACI", "Mortein"], GroceryType.PACKET, ["10pcs", "20pcs"], (60, 180)),
        ("Matchbox", ["Dhaka Match", "Sun"], GroceryType.PACKET, ["10pcs"], (15, 30)),
        ("Candle", ["Rupali", "Mukta"], GroceryType.PACKET, ["6pcs", "12pcs"], (40, 150)),
    ],
}


def wait_for_db() -> None:
    """Postgres has no healthcheck in compose, so poll until it accepts connections."""
    async def ping() -> None:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()

    for attempt in range(1, DB_WAIT_ATTEMPTS + 1):
        try:
            asyncio.run(ping())
            print("Database is ready ✓")
            return
        except Exception as exc:  # postgres still booting
            print(f"Waiting for database ({attempt}/{DB_WAIT_ATTEMPTS}): {exc.__class__.__name__}")
            time.sleep(1)
    raise RuntimeError("Database did not become ready in time")


def run_migrations() -> None:
    # sync call: migrations/env.py drives its own asyncio.run(), so it must not run inside an event loop
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    print("Migrations applied ✓")


# flattened so every product is equally likely (categories with more products get more rows)
PRODUCTS = [(category, *product) for category, products in CATALOG.items() for product in products]


def _random_grocery() -> dict:
    category, product, brands, grocery_type, sizes, (min_price, max_price) = random.choice(PRODUCTS)

    current_price = random.randint(min_price, max_price)
    current_seller = random.choice(SELLERS)
    # best price is never above the current price; when it is lower, another seller had it cheaper
    best_price = max(1, round(current_price * random.uniform(0.85, 1.0)))
    best_seller = current_seller if best_price == current_price else random.choice(SELLERS)

    brand = random.choice(brands)
    low_stock_threshold = random.randint(1, 5)
    return {
        "id": uuid.uuid4(),
        "name": f"{brand} {product} {random.choice(sizes)}",
        "brand": brand,
        "type": grocery_type,
        "current_price": current_price,
        "current_seller": current_seller,
        "low_stock_threshold": low_stock_threshold,
        "quantity_in_stock": random.randint(0, low_stock_threshold * 4),
        "should_include": random.random() < 0.3,
        "category": category,
        "best_seller": best_seller,
        "best_price": best_price,
    }


async def seed_groceries() -> None:
    async with engine.begin() as conn:
        existing = await conn.scalar(select(func.count()).select_from(Grocery))
        if existing:
            print(f"Grocery seed skipped ({existing} rows already present)")
            return

        started = time.perf_counter()
        for offset in range(0, SEED_COUNT, BATCH_SIZE):
            batch = [_random_grocery() for _ in range(min(BATCH_SIZE, SEED_COUNT - offset))]
            await conn.execute(insert(Grocery), batch)
        print(f"Grocery seed complete ✓ ({SEED_COUNT} rows in {time.perf_counter() - started:.1f}s)")
    await engine.dispose()


if __name__ == "__main__":
    wait_for_db()
    run_migrations()
    asyncio.run(seed_groceries())
