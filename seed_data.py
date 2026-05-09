from backend import ClientManager, ProductManager, StockManager, OrderManager, OrderItemManager, ShipmentManager

cm = ClientManager()
pm = ProductManager()
sm = StockManager()
om = OrderManager()
oim = OrderItemManager()
shipm = ShipmentManager()

# ---- Clients ----
client1 = cm.add("Acme Retail", "1200 Market St, Chicago, IL", "acme-support@acme.com")
client2 = cm.add("NorthStar Electronics", "88 King St, Toronto, ON", "contact@northstar.ca")
client3 = cm.add("BlueWave Apparel", "500 Sunset Blvd, Los Angeles, CA", "orders@bluewave.com")

# ---- Products ----
p1 = pm.add("Wireless Mouse", "2.4GHz ergonomic mouse", "WM-204")
p2 = pm.add("USB-C Cable 1m", "Fast charging cable", "UC-100")
p3 = pm.add("Laptop Sleeve 15in", "Neoprene protective sleeve", "LS-150")
p4 = pm.add("Bluetooth Keyboard", "Slim portable keyboard", "BK-330")

# ---- Stock ----
sm.add(p1.product_id, 120, "A1")
sm.add(p1.product_id, 80, "B3")

sm.add(p2.product_id, 300, "A2")

sm.add(p3.product_id, 15, "C1")   # Low stock on purpose

sm.add(p4.product_id, 5, "D4")    # Very low stock for testing

# ---- Orders ----
order1 = om.add(client1.client_id)
oim.add(order1.order_id, p1.product_id, 10)
oim.add(order1.order_id, p2.product_id, 25)
om.commit_order(order1.order_id)

order2 = om.add(client3.client_id)
oim.add(order2.order_id, p4.product_id, 2)
om.commit_order(order2.order_id)

# ---- Shipments ----
shipment1 = shipm.add(order1.order_id)
shipm.mark_as_shipped(shipment1.shipment_id)
shipm.mark_as_delivered(shipment1.shipment_id)

print("Database seeded successfully.")
