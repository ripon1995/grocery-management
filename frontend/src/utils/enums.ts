export const GroceryType = {
    WEIGHT: 'weight',
    SACK: 'sack',
    CAN: 'can',
    PIECE: 'piece'
} as const;

export type GroceryType = typeof GroceryType[keyof typeof GroceryType];

export const GroceryStockStatus = {
    IN_STOCK: 'in_stock',
    BELOW_STOCK: 'below_stock'
} as const;
export type GroceryStockStatus = typeof GroceryStockStatus[keyof typeof GroceryStockStatus];

export const BestSeller = {
    MEENA: 'meena',
    SHWAPNO: 'shwapno',
    LOCAL: 'local',
    COMILLA: 'comilla'
} as const;
export type BestSeller = typeof BestSeller[keyof typeof BestSeller];