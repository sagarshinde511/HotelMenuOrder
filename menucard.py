import streamlit as st
import mysql.connector
import pandas as pd

# Database Configuration
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# Database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
def fetch_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return []

def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Product deleted successfully!")
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")

def product_deletion_ui():
    st.title("🗑️ Delete a Product")

    products = fetch_products()
    if products:
        product_map = {f"{prod['name']} (ID: {prod['id']})": prod['id'] for prod in products}
        selected_product = st.selectbox("Select a product to delete", list(product_map.keys()))

        if st.button("Delete Product"):
            delete_product(product_map[selected_product])
            st.rerun()
    else:
        st.info("No products available to delete.")

def insert_product(name, amount, img_binary, group):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO products (name, amount, img, `group`) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, amount, img_binary, group))
    connection.commit()
    cursor.close()
    connection.close()

def authenticate_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT `group` FROM HotelStaff WHERE loginID = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user[0] if user else None
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return None

def fetch_orders(user_group):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT tableNo, Product, quantity, status FROM HotelOrder WHERE `group` = %s"
        cursor.execute(query, (user_group,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(orders, columns=['Table No.', 'Product', 'Quantity', 'Status']) if orders else None
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return None

def update_order_status(table_no, status, user_group):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update order status in HotelOrder
        cursor.execute("UPDATE HotelOrder SET status = %s WHERE tableNo = %s", (status, table_no))

        # Update order status in FinalOrder
        #cursor.execute("UPDATE FinalOrder SET Status = %s WHERE orderNo = %s", (status, table_no))

        # If the order is served, delete entry from GroupTable
        if status == "Served":
            
            cursor.execute("DELETE FROM HotelOrder WHERE tableNo = %s AND `group` = %s", (table_no, user_group))


        conn.commit()
        cursor.close()
        conn.close()
        st.success("Order status updated successfully!")

    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
def dashboard():
    st.title("📊 Dashboard")
    user_group = st.session_state.user_group  # Extract it once and reuse
    st.write(f"Welcome! Your group: **{st.session_state.user_group}**")
    orders_df = fetch_orders(st.session_state.user_group)
    if orders_df is not None:
        st.table(orders_df)
        table_numbers = orders_df['Table No.'].unique().tolist()
        selected_table = st.selectbox("Select Table Number", table_numbers)
        status_options = ["Received Order", "Processing", "Preparing Order", "Order Prepared", "Dispatched", "Served"]
        selected_status = st.selectbox("Update Order Status", status_options)
        if st.button("Update Status"):
            update_order_status(selected_table, selected_status, user_group)
            st.rerun()
    else:
        st.write("No orders found for your group.")

def login():
    st.title("🔒 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.session_state.user_group = "admin"
            st.rerun()
        else:
            user_group = authenticate_user(username, password)
            if user_group:
                st.session_state.authenticated = True
                st.session_state.user_group = user_group
                st.rerun()
            else:
                st.error("Invalid username or password.")

def register_product():
    st.title("📦 Product Registration")
    product_name = st.text_input("Product Name")
    product_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    product_image = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
    product_group = st.selectbox("Select Group", ["VegStarter", "NonVegStarter", "VegMainCource", "NonVegMainCource", "Roti", "Rice", "Beverage"])
    if st.button("Register Product"):
        if not product_name or product_amount <= 0 or not product_image or not product_group:
            st.error("All fields are required!")
        else:
            try:
                insert_product(product_name, product_amount, product_image.read(), product_group)
                st.success("Product registered successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

st.set_page_config(page_title="Hotel Management", page_icon="🏨", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_group" not in st.session_state:
    st.session_state.user_group = ""

# Tab Layout
tabs = st.tabs(["Login", "Dashboard", "Register Product", "Delet Product"])

with tabs[0]:
    login()

with tabs[1]:
    if st.session_state.authenticated:
        dashboard()
    else:
        st.warning("Please login first to view the dashboard.")

with tabs[2]:
    if st.session_state.authenticated:
        register_product()
    else:
        st.warning("Please login first to register a product.")
with tabs[3]:
    if st.session_state.authenticated:
        
        product_deletion_ui()
    else:
        st.warning("Please login first to register a product.")
