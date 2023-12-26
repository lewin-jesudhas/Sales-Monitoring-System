Welcome to our Sales Monitoring System for a milk parlour.

Overview:
        Developing a database system for a manufacturing company's sales monitoring, encompassing five regional offices, salespersons, wholesalers, and dealers.
        The system will efficiently manage product information, orders, payments, and facilitate communication between salespersons and dealers for streamlined operations.

Features:
- Barcode scanning at the time of adding new stock. The barcode id is the primary key in the products table.
- Changing the status of payment in the edit payments page.
- Updation of date and time of payment in the payments page.
- Calculating the sum of the payments received.

Dependencies:
- Oracle sql *plus 21c
- pip install cx_Oracle
- pip install flask
- pip install pyzbar
- (Replace your connection string in sales.py)


If you have issues installing cx_Oracle go to microsoft visual studio installer and install 
1. Desktop development with c++
2. .NET desktop build tools
3. Data storage and processing build tools

pip install wheel
