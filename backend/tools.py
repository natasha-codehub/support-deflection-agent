import json
import os
from typing import Optional
from config import MOCK_DATA_PATH

_orders: list[dict] = []
_accounts: list[dict] = []


def _load():
    global _orders, _accounts
    if not _orders:
        with open(os.path.join(MOCK_DATA_PATH, "orders.json")) as f:
            _orders = json.load(f)
    if not _accounts:
        with open(os.path.join(MOCK_DATA_PATH, "accounts.json")) as f:
            _accounts = json.load(f)


def orders_lookup(order_id: str) -> Optional[dict]:
    _load()
    order_id = order_id.strip().upper()
    for order in _orders:
        if order["order_id"].upper() == order_id:
            return {
                "order_id": order["order_id"],
                "status": order["status"],
                "eta": order.get("eta"),
                "location": order["location"],
                "items": order["items"],
                "account_name": order["account_name"],
                "invoice_id": order.get("invoice_id"),
                "shipped_date": order.get("shipped_date"),
                "billed_qty": order.get("billed_qty"),
                "delivered_qty": order.get("delivered_qty"),
                "short_pay_dispute": order.get("short_pay_dispute", False),
                "dispute_note": order.get("dispute_note"),
                "cancellation_reason": order.get("cancellation_reason"),
            }
    return None


def pod_lookup(order_id: str) -> Optional[dict]:
    _load()
    order_id = order_id.strip().upper()
    for order in _orders:
        if order["order_id"].upper() == order_id:
            if not order.get("has_pod"):
                return None
            return {
                "order_id": order["order_id"],
                "pod_url": order.get("pod_url", f"https://pods.acmeco.com/{order['order_id']}.pdf"),
                "delivery_date": order.get("delivery_date"),
                "signed_by": order.get("signed_by"),
                "location": order["location"],
                "invoice_id": order.get("invoice_id"),
            }
    return None


def account_lookup(account_id: str) -> Optional[dict]:
    _load()
    account_id = account_id.strip().upper()
    for account in _accounts:
        if account["account_id"].upper() == account_id:
            return account
    return None


def orders_by_account(account_id: str) -> list[dict]:
    _load()
    account_id = account_id.strip().upper()
    return [o for o in _orders if o["account_id"].upper() == account_id]
