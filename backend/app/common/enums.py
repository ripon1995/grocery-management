from enum import Enum


class GroceryType(Enum):
    WEIGHT = 'weight'
    SACK = 'sack'
    CAN = 'can'
    PIECE = 'piece'


class GroceryStockStatus(Enum):
    IN_STOCK = 'in_stock'
    BELOW_STOCK = 'below_stock'


class Seller(Enum):
    MEENA = 'meena'
    SHWAPNO = 'shwapno'
    LOCAL = 'local'
    COMILLA = 'comilla'
