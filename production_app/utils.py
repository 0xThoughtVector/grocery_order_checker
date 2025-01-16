"""
Utility functions, including the logic to compare recognized items to the order requirements.
"""

from typing import Dict, Tuple

def compare_order(recognized: Dict[str, int], required: Dict[str, int]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Compare recognized items vs. required (order) items.
    Returns:
       missing_dict: {item: quantity_missing}
       extra_dict:   {item: quantity_extra}
    If an item is recognized but not in required, it's extra.
    If an item in required is not recognized or recognized in fewer quantity, it's missing.
    """
    missing_dict = {}
    extra_dict = {}

    # 1. Check for missing or partial
    for req_item, req_qty in required.items():
        rec_qty = recognized.get(req_item, 0)
        if rec_qty < req_qty:
            missing_dict[req_item] = req_qty - rec_qty

    # 2. Check for extra
    for rec_item, rec_qty in recognized.items():
        req_qty = required.get(rec_item, 0)
        if rec_qty > req_qty:
            extra_dict[rec_item] = rec_qty - req_qty

    return missing_dict, extra_dict
