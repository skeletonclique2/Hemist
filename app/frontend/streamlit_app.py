import streamlit as st
import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = "http://localhost:8000/auth/login"

def login():
    st.title("AI Agents System - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(AUTH_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state["token"] = token
            st.success("Login successful!")
        else:
            st.error("Login failed. Check your credentials.")

def signup():
    st.title("AI Agents System - Signup")
    st.info("Signup is not yet implemented. Please contact admin.")

def logout():
    if "token" in st.session_state:
        del st.session_state["token"]
    st.success("Logged out successfully.")

def get_headers():
    token = st.session_state.get("token", None)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def show_dashboard():
    st.title("AI Agents Dashboard")
    st.write("Welcome to the AI Agents System dashboard.")
    
    # Fetch agents
    agents_resp = requests.get(f"{API_BASE_URL}/agents", headers=get_headers())
    if agents_resp.status_code == 200:
        agents = agents_resp.json()
        st.subheader("Agents")
        for agent in agents:
            st.write(f"- {agent['name']} ({agent['type']}) - Status: {agent['status']}")
    else:
        st.error("Failed to fetch agents. Please login again.")
    
    # Fetch workflows
    workflows_resp = requests.get(f"{API_BASE_URL}/workflows", headers=get_headers())
    if workflows_resp.status_code == 200:
        workflows = workflows_resp.json()
        st.subheader("Workflows")
        for wf in workflows:
            st.write(f"- {wf['name']} - Status: {wf['status']}")
    else:
        st.error("Failed to fetch workflows. Please login again.")
    
    if st.button("Logout"):
        logout()

def main():
    if "token" not in st.session_state:
        menu = ["Login", "Signup"]
        choice = st.sidebar.selectbox("Menu", menu)
        if choice == "Login":
            login()
        elif choice == "Signup":
            signup()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
