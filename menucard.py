import streamlit as st
import mysql.connector
import pandas as pd

# Database Configuration
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students1",
    "password": "testStudents@123",
    "database": "u263681140_students1"
}

# Database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

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
tabs = st.tabs(["Login", "Register Product"])

with tabs[0]:
    login()

with tabs[1]:
    if st.session_state.authenticated:
        register_product()
    else:
        st.warning("Please login first to register a product.")
