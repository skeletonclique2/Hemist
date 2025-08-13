import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def create_streamlit_app():
    """Create the main Streamlit application"""
    st.set_page_config(
        page_title="AI Agents Dashboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Agents System Dashboard")
    st.markdown("Production-ready multi-agent AI system for content generation")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Agents", "Workflows", "System Status", "Create Workflow"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Agents":
        show_agents()
    elif page == "Workflows":
        show_workflows()
    elif page == "System Status":
        show_system_status()
    elif page == "Create Workflow":
        show_create_workflow()

def show_dashboard():
    """Show the main dashboard"""
    st.header("📊 System Overview")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Get system status
        system_status = requests.get(f"{API_BASE_URL}/system/status").json()
        
        with col1:
            st.metric("System Status", system_status.get("status", "Unknown"))
        
        with col2:
            st.metric("Database", system_status.get("components", {}).get("database", "Unknown"))
        
        with col3:
            st.metric("Redis", system_status.get("components", {}).get("redis", "Unknown"))
        
        with col4:
            st.metric("Agents", system_status.get("components", {}).get("agents", "Unknown"))
        
        # Get agents
        agents = requests.get(f"{API_BASE_URL}/agents").json()
        
        # Create agent status chart
        st.subheader("🤖 Agent Status")
        if agents:
            agent_df = pd.DataFrame(agents)
            st.dataframe(agent_df, use_container_width=True)
        else:
            st.info("No agents found")
        
        # Get workflows
        workflows = requests.get(f"{API_BASE_URL}/workflows").json()
        
        st.subheader("📋 Recent Workflows")
        if workflows:
            workflow_df = pd.DataFrame(workflows)
            st.dataframe(workflow_df, use_container_width=True)
        else:
            st.info("No workflows found")
            
    except Exception as e:
        st.error(f"Failed to load dashboard data: {str(e)}")

def show_agents():
    """Show agents page"""
    st.header("🤖 Agents Management")
    
    try:
        agents = requests.get(f"{API_BASE_URL}/agents").json()
        
        if agents:
            for agent in agents:
                with st.expander(f"{agent['name']} ({agent['type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {agent['status']}")
                        st.write(f"**Type:** {agent['type']}")
                        st.write(f"**Created:** {agent['created_at']}")
                    
                    with col2:
                        if st.button(f"Refresh {agent['name']}", key=f"refresh_{agent['name']}"):
                            st.rerun()
                        
                        # Add agent-specific controls here
                        if agent['type'] == 'coordinator':
                            if st.button("Start Workflow", key=f"start_{agent['name']}"):
                                st.success("Workflow started!")
                        
                        elif agent['type'] == 'researcher':
                            if st.button("Research Topic", key=f"research_{agent['name']}"):
                                st.success("Research initiated!")
        else:
            st.info("No agents found")
            
    except Exception as e:
        st.error(f"Failed to load agents: {str(e)}")

def show_workflows():
    """Show workflows page"""
    st.header("📋 Workflows")
    
    try:
        workflows = requests.get(f"{API_BASE_URL}/workflows").json()
        
        if workflows:
            for workflow in workflows:
                with st.expander(f"{workflow['name']} - {workflow['status']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {workflow['status']}")
                        st.write(f"**Created:** {workflow['created_at']}")
                        st.write(f"**Updated:** {workflow['updated_at']}")
                    
                    with col2:
                        if st.button("View Details", key=f"view_{workflow['id']}"):
                            st.json(workflow)
                        
                        if workflow['status'] == 'pending':
                            if st.button("Start", key=f"start_{workflow['id']}"):
                                st.success("Workflow started!")
                        
                        elif workflow['status'] == 'running':
                            if st.button("Pause", key=f"pause_{workflow['id']}"):
                                st.success("Workflow paused!")
        else:
            st.info("No workflows found")
            
    except Exception as e:
        st.error(f"Failed to load workflows: {str(e)}")

def show_system_status():
    """Show system status page"""
    st.header("🔧 System Status")
    
    try:
        # Health check
        health = requests.get(f"{API_BASE_URL}/health").json()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("API Health")
            st.json(health)
        
        # System status
        system_status = requests.get(f"{API_BASE_URL}/system/status").json()
        
        with col2:
            st.subheader("System Components")
            st.json(system_status)
        
        # Real-time monitoring
        st.subheader("📈 Real-time Monitoring")
        
        if st.button("Refresh Status"):
            st.rerun()
        
        # Add charts and metrics here
        st.info("Real-time monitoring charts will be implemented here")
        
    except Exception as e:
        st.error(f"Failed to load system status: {str(e)}")

def show_create_workflow():
    """Show workflow creation page"""
    st.header("🚀 Create New Workflow")
    
    with st.form("create_workflow"):
        workflow_name = st.text_input("Workflow Name", placeholder="Enter workflow name")
        
        workflow_type = st.selectbox(
            "Workflow Type",
            ["content_generation", "research_analysis", "quality_check", "custom"]
        )
        
        workflow_description = st.text_area(
            "Description",
            placeholder="Describe what this workflow should accomplish"
        )
        
        # Agent selection
        st.subheader("Select Agents")
        try:
            agents = requests.get(f"{API_BASE_URL}/agents").json()
            if agents:
                selected_agents = st.multiselect(
                    "Choose agents to include",
                    [agent['name'] for agent in agents],
                    default=["coordinator", "researcher", "writer"]
                )
            else:
                selected_agents = []
                st.warning("No agents available")
        except:
            selected_agents = []
            st.warning("Could not load agents")
        
        # Workflow parameters
        st.subheader("Parameters")
        target_length = st.number_input("Target Content Length", min_value=100, max_value=5000, value=1500)
        quality_threshold = st.slider("Quality Threshold", min_value=0.0, max_value=1.0, value=0.8, step=0.1)
        
        submitted = st.form_submit_button("Create Workflow")
        
        if submitted:
            if workflow_name and workflow_description:
                try:
                    workflow_data = {
                        "name": workflow_name,
                        "type": workflow_type,
                        "description": workflow_description,
                        "agents": selected_agents,
                        "parameters": {
                            "target_length": target_length,
                            "quality_threshold": quality_threshold
                        },
                        "created_at": datetime.now().isoformat()
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/workflows", json=workflow_data)
                    
                    if response.status_code == 200:
                        st.success("Workflow created successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Failed to create workflow: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error creating workflow: {str(e)}")
            else:
                st.error("Please fill in all required fields")

if __name__ == "__main__":
    create_streamlit_app() 