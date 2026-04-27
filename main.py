"""This is the main file for the Inventory System Backend.
  It's a little long due to not having the front end just yet"""

from backend import (
    ClientManager,
    ProductManager,
    StockManager,
    OrderManager,
    OrderItemManager,
    ShipmentManager,
    ShipmentItemManager
)

def main():
    print("=== 3PL Inventory System Backend Test ===")

    # Instantiate managers
    clients = ClientManager()
    products = ProductManager()
    stock = StockManager()
    orders = OrderManager()
    order_items = OrderItemManager()
    shipments = ShipmentManager()
    shipment_items = ShipmentItemManager()

    # 1. Add a client
    client = clients.add("Test Client", "123 Test St", "test@example.com")
    print("Client added:", client.client_id, client.client_name)

    # 2. Add a product
    product = products.add("Laptop", "Dell XPS 13", "SKU123")
    print("Product added:", product.product_id, product.product_name)

    # 3. Add stock for that product
    stock_row = stock.add(product.product_id, 50, "Warehouse A")
    print("Stock added:", stock_row.stock_id, stock_row.quantity)

    # 4. Create an order for the client
    order = orders.add(client.client_id)
    print("Order created:", order.order_id)

    # 5. Add an item to the order
    item = order_items.add(order.order_id, product.product_id, 3)
    print("Order item added:", item.order_item_id)

    # 6. Commit the order
    orders.commit_order(order.order_id)
    print("Order status:", orders.fetch_by_id(order.order_id).order_status)

    # 7. Create a shipment for the order
    shipment = shipments.add(order.order_id)
    print("Shipment created:", shipment.shipment_id)

    # 8. Add shipment item
    ship_item = shipment_items.add(shipment.shipment_id, product.product_id, 3)
    print("Shipment item added:", ship_item.shipment_item_id)

    # 9. Mark shipment as shipped
    shipments.mark_as_shipped(shipment.shipment_id)
    print("Shipment status:", shipments.check_status(shipment.shipment_id))


if __name__ == "__main__":
    main()