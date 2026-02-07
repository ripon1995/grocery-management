from enum import Enum


class GroceryType(str, Enum):
    WEIGHT = 'weight'
    SACK = 'sack'
    CAN = 'can'
    PIECE = 'piece'


class GroceryStockStatus(str, Enum):
    IN_STOCK = 'in_stock'
    BELOW_STOCK = 'below_stock'


class Seller(str, Enum):
    MEENA = 'meena'
    SHWAPNO = 'shwapno'
    LOCAL = 'local'
    COMILLA = 'comilla'
