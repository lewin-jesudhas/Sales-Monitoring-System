from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import cx_Oracle
import csv
from pyzbar import pyzbar
import cv2

app = Flask(__name__)

# Replace 'your_oracle_connection_string' with your actual Oracle connection string
oracle_connection_string = 'your_oracle_connection_string'
#lsnrtcl services for host string
connection = cx_Oracle.connect(oracle_connection_string)

@app.route('/', methods=['GET', 'POST'])
def employee_login():
    # Employee login to access the dashboard
    if request.method == 'POST':
        employee_id = request.form.get("username", "")
        password = request.form.get("password", "")

        # Check if the employee exists in the employees list
        with open('employee_data.csv', 'r') as file:
            reader = csv.reader(file)
            for employee in reader:
                if employee[0] == employee_id and employee[1] == password:
                    return render_template('dashboard.html', employee=employee)

        error = 'Invalid employee ID or password'

        return render_template('index.html', error=error)
    
    return render_template('index.html')

@app.route('/employee/products')
def products():
    try:
        # Fetch data from the database
        cursor = connection.cursor()

        # Query for fetching Products data
        cursor.execute('SELECT * FROM Products')
        products_data = cursor.fetchall()
        
        # Close the cursor
        cursor.close()

        # Render the HTML template with the fetched data
        return render_template('display_stock.html', products=products_data)

    except Exception as e:
        # Print the error for debugging
        print("Error:", str(e))
        return "An error occurred while fetching data."

def draw_barcode(decoded, image):
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top), 
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image

def decode(image):
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        image = draw_barcode(obj, image)
        print("Data:", obj.data)
        print()

    return image, decoded_objects  # Return both image and decoded_objects

def capture_and_decode_barcode():
    # Open a connection to the webcam
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frames from the webcam
        ret, frame = cap.read()

        if not ret:
            break

        # Decode barcodes from the frame
        _, decoded_objects = decode(frame)

        # Check if there is a barcode in the frame
        if decoded_objects:
            # Return the first detected barcode data
            barcode_data = decoded_objects[0].data.decode('utf-8')
            break

        # Display the frame (optional)
        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    # Release the webcam
    cap.release()
    # Close any open windows (optional)
    cv2.destroyAllWindows()

    return barcode_data if decoded_objects else None


@app.route('/employee/add_stock', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        # Automatically open the webcam and decode barcode
        barcode_data = capture_and_decode_barcode()

        # Update the barcode input field with the scanned data
        if barcode_data:
            request.form = request.form.to_dict()
            request.form['barcode_data'] = barcode_data
        else:
            print("No barcode detected.")

        # Extract other form data
        quantity = int(request.form['quantity'])
        product_name = request.form['product_name']
        price = float(request.form['price'])

        cursor = connection.cursor()

        try:
            # Call the stored procedure to add stock
            cursor.callproc('ADD_STOCK_PROC', (barcode_data, product_name, price, quantity))
        finally:
            cursor.close()

        return redirect(url_for('display_stock'))

    return render_template('add_stock.html')

@app.route('/display_stock')
def display_stock():
    # Fetch data from the database (Products table)
    cursor = connection.cursor()
    query = 'SELECT * FROM Products'
    cursor.execute(query)
    products_data = cursor.fetchall()
    cursor.close()

    # Render the HTML page with the products data
    return render_template('display_stock1.html', products=products_data)

@app.route('/regionaloffice')
def region():
    try:
        # Fetch data from the database
        cursor = connection.cursor()

        # Example query for fetching Products data
        cursor.execute('SELECT * FROM RegionalOffices')
        regional_off = cursor.fetchall()
        
        # Close the cursor
        cursor.close()

        # Render the HTML template with the fetched data
        return render_template('regional_office.html', RegionalOffices=regional_off)

    except Exception as e:
        # Print the error for debugging
        print("Error:", str(e))
        return "An error occurred while fetching data."

@app.route('/payments')
def display_payments():
    cursor = connection.cursor()

    # Fetch data from the database (joining Payments, Orders, Dealers, and Salespersons)
    query = '''
    SELECT Payments.PaymentID, Payments.Amount, Payments.PaymentDate, Payments.PaymentMode, Payments.PaymentStatus,
           Orders.OrderID, Orders.Quantity, Orders.OrderDate,
           Dealers.DealerID, Salespersons.SalespersonID
    FROM Payments
    JOIN Orders ON Payments.OrderID = Orders.OrderID
    JOIN Dealers ON Orders.DealerID = Dealers.DealerID
    JOIN Salespersons ON Orders.SalespersonID = Salespersons.SalespersonID
'''
    cursor.execute(query)
    payments_data = cursor.fetchall()
    cursor.close()


    # Render the HTML page with the payments data
    return render_template('payment_total.html', payments=payments_data)

@app.route('/salespersons')
def display_salespersons():
    cursor = connection.cursor()

    # Fetch data from the database (Salespersons table)
    query = 'SELECT * FROM Salespersons'
    cursor.execute(query)
    salespersons_data = cursor.fetchall()
    cursor.close()

    # Render the HTML page with the salespersons data
    return render_template('salespersons.html', salespersons=salespersons_data)

@app.route('/add_salesperson', methods=['GET', 'POST'])
def add_salesperson():
    if request.method == 'POST':
        # Extract data from the form submission
        salesperson_id = int(request.form['salesperson_id'])
        name = request.form['name']
        contact_info = request.form['contact_info']
        region_id = int(request.form['region_id'])
        training_progress = request.form['training_progress']
        incentives = float(request.form['incentives'])

        # Call the stored procedure to insert the new salesperson
        cursor = connection.cursor()
        try:
            cursor.callproc('insert_salesperson', (salesperson_id, name, contact_info, region_id, training_progress, incentives))
            connection.commit()  # Commit the transaction
        finally:
            cursor.close()

        return redirect(url_for('display_salespersons'))

    return render_template('add_saleperson.html')

@app.route('/dealers')
def display_dealers():
    cursor = connection.cursor()

    # Fetch data from the database (dealers table)
    query = 'SELECT * FROM Dealers'
    cursor.execute(query)
    dealers_data = cursor.fetchall()
    cursor.close()

    # Render the HTML page with the dealers data
    return render_template('dealers.html', dealers=dealers_data)


@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    cursor = connection.cursor()

    if request.method == 'POST':
        data = request.form
        product_id = int(data['product_id'])
        dealer_id = int(data['dealer_id'])
        salesperson_id = int(data['salesperson_id'])
        quantity = int(data['quantity'])
        payment_mode = data['payment_mode']
        payment_status = data['payment_status']

        try:
            # Check if the salesperson and dealer are in the same region
            cursor.execute("""
                SELECT 1
                FROM Salespersons s
                JOIN Dealers d ON s.RegionID = d.RegionID
                WHERE s.SalespersonID = :salesperson_id AND d.DealerID = :dealer_id
            """, salesperson_id=salesperson_id, dealer_id=dealer_id)

            result = cursor.fetchone()

            if not result:
                return render_template('place_order2.html', error="Salesperson and dealer are not in the same region")

            # Check if there is enough quantity in stock
            cursor.execute("SELECT Quantity, Price FROM Products WHERE ProductID = :product_id", product_id=product_id)
            result = cursor.fetchone()

            current_quantity = result[0]
            product_price = result[1]

            if quantity > current_quantity:
                return render_template('place_order2.html', error="Insufficient quantity in stock")

            # Insert the order
            cursor.execute("""
                INSERT INTO Orders (ProductID, DealerID, SalespersonID, Quantity, OrderDate)
                VALUES (:product_id, :dealer_id, :salesperson_id, :quantity, CURRENT_DATE)
            """, product_id=product_id, dealer_id=dealer_id, salesperson_id=salesperson_id, quantity=quantity)

            # Get the order ID
            cursor.execute("SELECT order_id_seq.CURRVAL FROM dual")
            order_id = cursor.fetchone()[0]

            # Reduce the quantity in the Products table
            updated_quantity = current_quantity - quantity
            cursor.execute("UPDATE Products SET Quantity = :updated_quantity WHERE ProductID = :product_id",
                           updated_quantity=updated_quantity, product_id=product_id)

            # Calculate the total amount
            total_amount = quantity * product_price

            # Insert payment details into Payments table
            cursor.execute("""
                INSERT INTO Payments (OrderID, Amount, PaymentDate, PaymentMode, PaymentStatus)
                VALUES (:order_id, :amount, CURRENT_DATE, :payment_mode, :payment_status)
            """, order_id=order_id, amount=total_amount, payment_mode=payment_mode, payment_status=payment_status)

            return render_template('place_order2.html', message="Order placed successfully", total_amount=total_amount)

        except cx_Oracle.Error as e:
            error_message = f"Oracle Error: {e}"
            return render_template('place_order2.html', error=error_message)

        finally:
            connection.commit()
            cursor.close()

    # Return a response for the 'GET' case
    return render_template('place_order2.html')

@app.route('/edit_payments', methods=['GET', 'POST'])
def edit_payments():
    cursor = connection.cursor()

    if request.method == 'POST':
        order_id = int(request.form.get('order_id'))
        new_payment_status = request.form.get('payment_status')

        try:
            # Update the payment status in the Payments table
            cursor.execute("""
                UPDATE Payments
                SET PaymentStatus = :new_payment_status
                WHERE OrderID = :order_id
            """, new_payment_status=new_payment_status, order_id=order_id)

            connection.commit()

            return render_template('edit_payments.html', message="Payment status updated successfully")

        except cx_Oracle.Error as e:
            error_message = f"Oracle Error: {e}"
            return render_template('edit_payments.html', error=error_message)

        finally:
            cursor.close()

    # Fetch orders with payment status other than 'Complete'
    cursor.execute("""
        SELECT O.OrderID, P.PaymentStatus
        FROM Orders O
        JOIN Payments P ON O.OrderID = P.OrderID
        WHERE P.PaymentStatus <> 'Complete'
    """)
    orders = cursor.fetchall()
    return render_template('edit_payments.html', orders=orders)
    
if __name__ == '__main__':
    app.run(debug=True)
