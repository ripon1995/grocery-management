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
