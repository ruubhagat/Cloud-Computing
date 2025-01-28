from typing import List, Dict, Optional
from functools import lru_cache
import asyncio
from dataclasses import dataclass
from . import dao
from products import Product

@dataclass(frozen=True)
class BrowseItem:
    id: int
    name: str
    category: str
    price: float
    description: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BrowseItem':
        return cls(**data)

class BrowseService:
    def __init__(self):
        self._cache = {}
    
    @lru_cache(maxsize=2000)
    async def get_items(self, category: Optional[str] = None) -> List[BrowseItem]:
        items = await dao.get_browse_items(category)
        return [BrowseItem.from_dict(item) for item in items] if items else []
    
    @lru_cache(maxsize=100)
    async def get_categories(self) -> List[str]:
        return await dao.get_categories() or []
    
    async def get_featured_items(self, limit: int = 10) -> List[BrowseItem]:
        items = await dao.get_featured_items(limit)
        return [BrowseItem.from_dict(item) for item in items] if items else []
    
    async def search_items(self, query: str, limit: int = 50) -> List[BrowseItem]:
        results = await dao.search_items(query, limit)
        return [BrowseItem.from_dict(item) for item in results] if results else []
    
    async def batch_get_items(self, item_ids: List[int]) -> List[BrowseItem]:
        items = await asyncio.gather(*[dao.get_item(id_) for id_ in set(item_ids)])
        return [BrowseItem.from_dict(item) for item in items if item]
    
    def clear_cache(self):
        self.get_items.cache_clear()
        self.get_categories.cache_clear()

# Global instance
browse_service = BrowseService()
