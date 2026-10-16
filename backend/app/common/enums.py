from enum import Enum


class GroceryType(str, Enum):
    WEIGHT = 'weight'
    SACK = 'sack'
    CAN = 'can'
    PIECE = 'piece'
    PACKET = 'packet'
    BOTTLE = 'bottle'


class GroceryStockStatus(str, Enum):
    IN_STOCK = 'in_stock'
    BELOW_STOCK = 'below_stock'


class GroceryCategory(str, Enum):
    TOILETRIES = 'toiletries'
    FOOD = 'food'
    COOKIES = 'cookies'
    OIL = 'oil'
    OTHER = 'other'


class Seller(str, Enum):
    MEENA = 'meena'
    SHWAPNO = 'shwapno'
    LOCAL = 'local'
    COMILLA = 'comilla'
    DEFAULT = 'default'
    AGORA = 'agora'
    ONLINE = 'online'
    CHALDAL = 'chaldal'


# shops Gemini explore / campaign crawler work with (Phase 6)
MARKET_SHOPS = (Seller.SHWAPNO, Seller.CHALDAL, Seller.MEENA)


class PriceSource(str, Enum):
    MANUAL = 'manual'
    GEMINI = 'gemini'
    CAMPAIGN = 'campaign'


class ExploreJobStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'
