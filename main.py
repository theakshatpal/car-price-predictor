import streamlit as st
import pickle
import json
import os

# ---------- File path for users ----------
USER_FILE = "users.json"

# ---------- Load users from file ----------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {"admin": "1234", "user": "password"}  # default users

# ---------- Save users to file ----------
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------- Always load latest users here ----------
users = load_users()

# ---------- Session management ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------- Auth UI ----------
st.sidebar.title("🔐 User Access")
auth_mode = st.sidebar.selectbox("Choose Option", ["Login", "Create Account"])

if auth_mode == "Create Account":
    st.sidebar.markdown("### Create New Account")
    new_user = st.sidebar.text_input("New Username")
    new_pass = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Create Account"):
        if new_user in users:
            st.sidebar.error("🚫 Username already exists.")
        elif new_user == "" or new_pass == "":
            st.sidebar.warning("Please fill both fields.")
        else:
            users[new_user] = new_pass
            save_users(users)
            st.sidebar.success("✅ Account created! You can now log in.")

elif auth_mode == "Login":
    st.sidebar.markdown("### Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.sidebar.success(f"✅ Welcome, {username}!")
        else:
            st.sidebar.error("❌ Invalid username or password.")

# ---------- Logout ----------
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

# ---------- Stop if not logged in ----------
if not st.session_state.logged_in:
    st.stop()

# ---------- Load model ----------
model = pickle.load(open("model.pkl", "rb"))

# ---------- Main App ----------
st.title("🚘 Car Price Predictor")
st.markdown("Enter the details of the car below to get an estimated resale price:")

fuel_map = {"CNG": 1, "Diesel": 2, "Petrol": 3}
ownership_map = {"First": 1, "Second": 2, "Third or more": 3}
trans_map = {"Manual": 1, "Automatic": 2}

col1, col2 = st.columns(2)

with col1:
    fuel_type = st.selectbox("Fuel Type", list(fuel_map.keys()))
    ownership = st.selectbox("Ownership", list(ownership_map.keys()))
    transmission = st.selectbox("Transmission", list(trans_map.keys()))
    manufacture_year = st.slider("Manufacture Year", 1990, 2025, 2015)

with col2:
    kms_driven = st.number_input("Kilometers Driven", min_value=0, max_value=500000, value=40000, step=1000)
    mileage = st.number_input("Mileage (km/l)", min_value=5.0, max_value=50.0, value=18.0, step=0.5)
    engine = st.number_input("Engine Capacity (cc)", min_value=600, max_value=5000, value=1200, step=100)

if st.button("🔍 Predict Price"):
    features = [[
        fuel_map[fuel_type],
        kms_driven,
        ownership_map[ownership],
        trans_map[transmission],
        manufacture_year,
        mileage,
        engine
    ]]
    price = model.predict(features)[0]
    st.success(f"💰 Estimated Price: ₹{price:,.2f} Lakhs")

st.markdown("---")
st.caption("Made with ❤️ | Car Price Predictor App")
