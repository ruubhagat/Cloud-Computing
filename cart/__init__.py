import json
from cart import dao
from products import Product
from functools import lru_cache
from typing import List, Dict
import asyncio

class Cart:
    def __init__(self, id: int, username: str, contents: List[Product], cost: float):
        self.id = id
        self.username = username
        self.contents = contents
        self.cost = cost

    @staticmethod
    def load(data: Dict):
        products_list = [Product(**item) for item in json.loads(data['contents'])]
        return Cart(data['id'], data['username'], products_list, data['cost'])

@lru_cache(maxsize=1000)
async def get_cart(username: str) -> List[Product]:
    cart_details = await dao.get_cart(username)
    if not cart_details:
        return []

    # Batch product fetching
    product_ids = set()
    for cart_detail in cart_details:
        product_ids.update(json.loads(cart_detail['contents']))

    # Fetch all products in one go
    products = await asyncio.gather(*[products.get_product(product_id) for product_id in product_ids])
    
    return products

async def add_to_cart(username: str, product_id: int):
    await dao.add_to_cart(username, product_id)
    get_cart.cache_clear()  # Invalidate cache after modifying the cart

async def remove_from_cart(username: str, product_id: int):
    await dao.remove_from_cart(username, product_id)
    get_cart.cache_clear()  # Invalidate cache after modifying the cart

async def delete_cart(username: str):
    await dao.delete_cart(username)
    get_cart.cache_clear()  # Invalidate cache after modifying the cart