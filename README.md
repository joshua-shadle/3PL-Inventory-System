# 3PL Inventory System
SDEV Final Project
📦 3PL Inventory Management System
A desktop application built with Python, Tkinter, and SQLAlchemy that simulates a real-world Third‑Party Logistics (3PL) workflow.
It includes product management, client management, stock tracking, order creation, shipment handling, and reporting.

🚀 Features
🛒 Product & Inventory Management
Add, update, and delete products

Track SKU, quantity, and warehouse location

Automatic stock aggregation across multiple locations

Low‑stock alerts

Inventory report with quantities and locations

👥 Client Management
Add, update, and delete clients

Store name, address, and contact info

Predictive search when creating orders

📦 Order Management
Create orders linked to clients

Add items to orders

Commit orders

View total items per order

Delete orders (with automatic cleanup of order items & shipments)

🚚 Shipment Management
Create shipments from orders

Mark shipments as Shipped or Delivered

Delete shipments

Auto-refreshing shipment list

📊 Reporting
Inventory report

Low stock report

Global search bar for products, clients, orders, and shipments

🧱 Tech Stack
Component	Technology
GUI	Tkinter
Database ORM	SQLAlchemy
Database	SQLite
Architecture	MVC-style managers + screens
Language	Python 3


📂 Project Structure
Code
3PL-Inventory-System/
│
├── fntend.py            # Main Tkinter application (UI)
├── backend.py           # Managers for Products, Clients, Orders, Stock, Shipments
├── database.py          # SQLAlchemy models + engine + session
├── db.sqlite            # SQLite database file
└── README.md            # Project documentation
🛠️ Installation & Setup
1. Clone the repository
bash
git clone https://github.com/YOUR-USERNAME/3PL-Inventory-System.git
cd 3PL-Inventory-System
2. Create a virtual environment
bash
python -m venv venv
Activate it:

Windows

bash
venv\Scripts\activate
Mac/Linux

bash
source venv/bin/activate
3. Install dependencies
bash
pip install sqlalchemy
(Tkinter comes preinstalled with Python on Windows/macOS.)

4. Run the application
bash
python fntend.py
🗄️ Database Schema Overview
The system uses SQLAlchemy ORM with the following tables:

Client

Product

Stock

Order

OrderItem

Shipment

ShipmentItem

Each table is linked with proper foreign keys and relationships.

🧠 How It Works
Managers (backend.py)
Each entity (Product, Client, Order, etc.) has a dedicated manager class that handles:

CRUD operations

Business logic

Database queries

Screens (fntend.py)
Each section of the app (Products, Clients, Orders, Shipments, Reports) is a Tkinter Frame that:

Displays data

Provides forms

Calls backend managers

Database (database.py)
Defines all SQLAlchemy models and relationships.

🧪 Future Improvements
Shipment item management

Stock transfers between locations

CSV export for reports

User authentication

Dark mode

🤝 Contributing
Pull requests are welcome.
For major changes, please open an issue first to discuss what you’d like to change.

📜 License
This project is open-source and available under the MIT License.
