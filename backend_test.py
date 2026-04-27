# tests/test_backend.py

import pytest
from backend import (
    ClientManager,
    ProductManager,
    StockManager,
    OrderManager,
    OrderItemManager,
    ShipmentManager,
    ShipmentItemManager
)

@pytest.fixture
def clients():
    return ClientManager()

@pytest.fixture
def products():
    return ProductManager()

@pytest.fixture
def stock():
    return StockManager()

@pytest.fixture
def orders():
    return OrderManager()

@pytest.fixture
def order_items():
    return OrderItemManager()

@pytest.fixture
def shipments():
    return ShipmentManager()

@pytest.fixture
def shipment_items():
    return ShipmentItemManager()


def test_client_add_and_fetch(clients):
    c = clients.add("John Doe", "123 Street", "john@example.com")
    fetched = clients.fetch_by_id(c.client_id)
    assert fetched.client_name == "John Doe"


def test_product_add_and_fetch(products):
    p = products.add("Laptop", "Dell XPS", "SKU123")
    fetched = products.fetch_by_id(p.product_id)
    assert fetched.sku == "SKU123"


def test_stock_add_and_level(products, stock):
    p = products.add("Mouse", "Wireless", "SKU999")
    stock.add(p.product_id, 5, "A1")
    stock.add(p.product_id, 7, "A2")
    assert stock.stock_level(p.product_id) == 12


def test_order_and_items(clients, products, orders, order_items):
    c = clients.add("Client", "Addr", "Contact")
    p = products.add("Keyboard", "Mechanical", "SKU777")
    o = orders.add(c.client_id)
    item = order_items.add(o.order_id, p.product_id, 3)
    assert item.quantity == 3


def test_shipment_flow(clients, products, orders, order_items, shipments, shipment_items):
    c = clients.add("Client", "Addr", "Contact")
    p = products.add("Monitor", "4K", "SKU555")
    o = orders.add(c.client_id)
    order_items.add(o.order_id, p.product_id, 2)

    s = shipments.add(o.order_id)
    shipment_items.add(s.shipment_id, p.product_id, 2)

    shipments.mark_as_shipped(s.shipment_id)
    assert shipments.check_status(s.shipment_id) == "shipped"
