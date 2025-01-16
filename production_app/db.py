"""
Example minimal DB logic using SQLAlchemy.
We'll store orders in a simple table: orders, items in a separate table or 
serialized in a single column. For brevity, we show an in-memory approach with 
a dictionary. Modify to your real DB schema as needed.
"""

from typing import Dict, Any

# For a real DB, you'd do:
# from sqlalchemy import create_engine, Column, Integer, String, ...
# from sqlalchemy.orm import sessionmaker

# In a real environment, you'd create models like:
# class Order(Base):
#     __tablename__ = 'orders'
#     id = Column(Integer, primary_key=True)
#     items = Column(String)  # maybe store as JSON
#
# etc.

# ---------------------------------------------------------------------------
# 1. Example in-memory store (NOT production scale; for demonstration only).
# ---------------------------------------------------------------------------
ORDERS_DB = {
    101: {"Coke": 2, "Chips": 1},
    102: {"Eggs": 12, "Orange Juice": 1, "Bread": 2}
    # etc.
}

def get_order_by_id(order_id: int) -> Dict[str, int]:
    """
    Return the required items for the given order_id. 
    E.g., { "Coke": 2, "Chips": 1 } 
    or None if not found.
    """
    return ORDERS_DB.get(order_id, None)
