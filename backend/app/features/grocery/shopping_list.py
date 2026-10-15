"""
Shopping list built from groceries with should_include=True.

Pure functions only (no DB, no HTTP), so the rules are easy to read and check:
    • quantity_to_buy = max(low_stock_threshold - quantity_in_stock, 1)
    • each item is bought where it's cheapest (best_seller / best_price),
      falling back to current_seller / current_price when there is no best yet
    • rows grouped by shop, with a subtotal per shop and a grand total
"""
import csv
import io
from dataclasses import dataclass, field
from typing import Iterable, List

from app.common.enums import Seller
from app.features.grocery.models import Grocery

CSV_HEADER = ["shop", "name", "brand", "type", "quantity_to_buy", "unit_price", "line_total"]


@dataclass
class ShoppingListRow:
    name: str
    brand: str
    type: str
    quantity_to_buy: int
    unit_price: int

    @property
    def line_total(self) -> int:
        return self.quantity_to_buy * self.unit_price


@dataclass
class ShopGroup:
    shop: Seller
    rows: List[ShoppingListRow] = field(default_factory=list)

    @property
    def subtotal(self) -> int:
        return sum(row.line_total for row in self.rows)


@dataclass
class ShoppingList:
    shops: List[ShopGroup]

    @property
    def grand_total(self) -> int:
        return sum(group.subtotal for group in self.shops)


def quantity_to_buy(grocery: Grocery) -> int:
    # an item marked for the list but above its threshold is still wanted, so at least 1
    return max(grocery.low_stock_threshold - grocery.quantity_in_stock, 1)


def shop_and_price(grocery: Grocery) -> tuple[Seller, int]:
    if grocery.best_seller != Seller.DEFAULT and grocery.best_price:
        return grocery.best_seller, grocery.best_price
    return grocery.current_seller, grocery.current_price


def build_shopping_list(groceries: Iterable[Grocery]) -> ShoppingList:
    groups: dict[Seller, ShopGroup] = {}
    for grocery in groceries:
        shop, price = shop_and_price(grocery)
        groups.setdefault(shop, ShopGroup(shop=shop)).rows.append(
            ShoppingListRow(
                name=grocery.name,
                brand=grocery.brand,
                type=grocery.type.value,
                quantity_to_buy=quantity_to_buy(grocery),
                unit_price=price,
            )
        )

    for group in groups.values():
        group.rows.sort(key=lambda row: (row.name.lower(), row.brand.lower()))
    return ShoppingList(shops=sorted(groups.values(), key=lambda group: group.shop.value))


def shopping_list_to_csv(shopping_list: ShoppingList) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for group in shopping_list.shops:
        shop = group.shop.value.title()
        for row in group.rows:
            writer.writerow([shop, row.name, row.brand, row.type, row.quantity_to_buy, row.unit_price, row.line_total])
        writer.writerow([shop, "Subtotal", "", "", "", "", group.subtotal])
    writer.writerow(["", "Grand total", "", "", "", "", shopping_list.grand_total])
    return buffer.getvalue()
