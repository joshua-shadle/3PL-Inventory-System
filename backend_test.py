from backend import ProductManager, StockManager, ClientManager, OrderManager, OrderItemManager, ShipmentManager
from database import session, Product, Stock, Client, Order, Shipment

def setup_function():
    # Clear DB before each test
    session.query(Shipment).delete()
    session.query(Order).delete()
    session.query(Client).delete()
    session.query(Stock).delete()
    session.query(Product).delete()
    session.commit()

def test_inventory_report_data():
    pm = ProductManager()
    sm = StockManager()

    p = pm.add("Test Item", "Desc", "TI-001")
    sm.add(p.product_id, 50, "A1")
    sm.add(p.product_id, 25, "B2")

    total = sm.stock_level(p.product_id)
    assert total == 75

def test_low_stock_logic():
    pm = ProductManager()
    sm = StockManager()

    p = pm.add("LowStockItem", "desc", "LS-10")
    sm.add(p.product_id, 3, "C1")

    alerts = sm.low_stock_alert(threshold=10)
    assert len(alerts) == 1
    assert alerts[0]["product_name"] == "LowStockItem"
    assert alerts[0]["quantity"] == 3

def test_order_and_shipment_flow():
    cm = ClientManager()
    om = OrderManager()
    oim = OrderItemManager()
    shipm = ShipmentManager()

    client = cm.add("Test Client", "123 Road", "test@test.com")
    order = om.add(client.client_id)

    oim.add(order.order_id, 1, 5)
    om.commit_order(order.order_id)

    shipment = shipm.add(order.order_id)
    shipm.mark_as_shipped(shipment.shipment_id)
    shipm.mark_as_delivered(shipment.shipment_id)

    assert shipm.check_status(shipment.shipment_id) == "delivered"
