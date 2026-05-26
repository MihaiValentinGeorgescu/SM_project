import streamlit as st
from google import genai
from google.genai import types
import yaml
import datetime  
import uuid  # NEW: Imports a library to generate unique ID numbers for our database rows

# initialize with gemini token
client = genai.Client(api_key="paste token here")

# --- 1. STATE INITIALIZATION (Including Login) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "history_db" not in st.session_state:
    st.session_state["history_db"] = []

# --- SYSTEM PROMPTS ---
K8S_GENERATE_PROMPT = """
You are an expert Kubernetes Platform Engineer and DevOps assistant. 
Your job is to generate highly optimized, secure, and production-ready Kubernetes manifests based on user requests.

Rules:
1. Return the valid YAML manifest inside a standard markdown code block.
2. After the YAML block, provide a section called "🛠️ Suggested Improvements & Best Practices".
3. In the improvements section, suggest cloud-native best practices specific to their request (e.g., adding resource limits, liveness/readiness probes, securityContext, network policies, or labels).
4. If the user's request lacks critical production pieces (like missing ports or image tags), infer smart defaults but highlight them in your suggestions.
5. Do not include long conversational fluff. Be direct and technical.
"""

K8S_DEBUG_PROMPT = """
You are an expert Kubernetes troubleshooter. The user will provide an error log, a `kubectl` error statement, or a status description (like CrashLoopBackOff, ImagePullBackOff, CreateContainerConfigError).

Your job is to:
1. Briefly explain **why** this error happens in plain, clear language.
2. Provide a bulleted list of **actionable steps** to fix the issue.
3. If applicable, provide the exact `kubectl` troubleshooting commands they should run to investigate further (e.g., `kubectl describe pod ...`, `kubectl logs ...`).
Be direct, highly technical, and concise. Do not use conversational filler.
"""

st.set_page_config(page_title="K8s AI Toolkit", page_icon="☸️", layout="wide")

# log8in flow

if not st.session_state["logged_in"]:
    st.title("🔒 K8s Developer Toolkit Login")
    st.write("Please log in to access the AI assistant and your local database.")
    
    # Create a small, centered box for the login
    login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
    with login_col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Log In 🔑", use_container_width=True):
            # Hardcoded credentials for demonstration
            if username == "admin" and password == "password123":
                st.session_state["logged_in"] = True
                st.rerun()  # Refresh the page to bypass the login screen
            else:
                st.error("❌ Invalid username or password.")

# Only runs if logged in

else:
    # --- 2. BACKEND HISTORY SIDEBAR (With Update & Delete) ---
    with st.sidebar:
        st.header("📜 Activity History Log")
        
        # Logout Button
        if st.button("Log Out 🚪", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()
            
        st.write("---")
        
        # Clear All (Bulk Delete)
        if st.button("Clear All History 🗑️", use_container_width=True):
            st.session_state["history_db"] = []
            st.rerun()
            
        st.write("---")
        
        if not st.session_state["history_db"]:
            st.caption("No operations recorded yet.")
        else:
            # Loop backwards through history
            for entry in reversed(st.session_state["history_db"]):
                with st.expander(f"{entry['icon']} {entry['title']}"):
                    st.caption(f"🕒 Time: {entry['timestamp']}")
                    
                    # ✏️ UPDATE (Read & Edit the text)
                    edited_content = st.text_area(
                        "Edit Output Log:", 
                        value=entry['content'], 
                        height=200, 
                        key=f"edit_{entry['id']}" # Uses the unique ID so Streamlit doesn't get confused
                    )
                    
                    # Layout buttons side-by-side
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        # 💾 UPDATE ACTION
                        if st.button("Save", key=f"save_{entry['id']}", use_container_width=True):
                            # Find the exact item in our RAM array and update its content
                            for item in st.session_state["history_db"]:
                                if item["id"] == entry["id"]:
                                    item["content"] = edited_content
                            st.success("Saved!")
                            
                    with btn_col2:
                        # 🗑️ DELETE ACTION
                        if st.button("Delete", key=f"del_{entry['id']}", type="primary", use_container_width=True):
                            # Rebuild the list without this specific ID
                            st.session_state["history_db"] = [i for i in st.session_state["history_db"] if i["id"] != entry["id"]]
                            st.rerun() # Refresh to make it disappear instantly

    # Main headers
    st.title("☸️ Kubernetes AI Developer Toolkit")
    st.caption("A simple AI-powered suite to generate, validate, and debug your Kubernetes manifests.")

    # Create three distinct tabs for our tools
    tab1, tab2, tab3 = st.tabs(["✨ Generate Manifest", "✅ Validate YAML", "🔍 Debug K8s Errors"])

    # tab 1: generate manifest
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Describe Your Deployment")
            manifest_type = st.selectbox("What are we building?", ["Deployment + Service", "Deployment Only", "StatefulSet", "ConfigMap/Secret", "Ingress"])
            app_name = st.text_input("Application Name", value="my-web-app")
            image_name = st.text_input("Container Image", value="nginx:latest")
            container_port = st.number_input("Container Port", value=80)
            additional_details = st.text_area("Additional Details / Custom Requests", key="gen_details")
            generate_btn = st.button("Generate Manifest 🚀", type="primary")

        with col2:
            st.subheader("Generated Manifest & Suggestions")
            if generate_btn:
                user_prompt = f"Please create a Kubernetes {manifest_type} for an application named '{app_name}'.\n- Container Image: {image_name}\n- Container Port: {container_port}\n- Additional Requirements: {additional_details}"
                with st.spinner("Gemini is analyzing and generating manifests..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=user_prompt,
                            config=types.GenerateContentConfig(system_instruction=K8S_GENERATE_PROMPT, temperature=0.2)
                        )
                        st.markdown(response.text)
                        
                        # 🟢 CREATE ACTION: Save to in-memory storage array with a Unique ID
                        new_log = {
                            "id": str(uuid.uuid4()),  # Automatically generates a random string like '123e4567-e89b-12d3'
                            "icon": "✨",
                            "title": f"{manifest_type}: {app_name}",
                            "content": response.text,
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state["history_db"].append(new_log)
                        st.rerun()  
                        
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    # tab 2: validate yaml
    with tab2:
        st.subheader("Syntax & Structural Validator")
        yaml_input = st.text_area("Paste YAML Manifest here:", height=300, placeholder="apiVersion: apps/v1\nkind: Deployment\n...")
        validate_btn = st.button("Validate YAML ✅", type="primary")
        
        if validate_btn:
            if not yaml_input.strip():
                st.warning("Please paste some YAML code first.")
            else:
                try:
                    parsed_yaml = yaml.safe_load(yaml_input)
                    if parsed_yaml is None or not isinstance(parsed_yaml, dict):
                        st.error("❌ Invalid format: The input is not structured as a valid Kubernetes object mapping.")
                    else:
                        st.success("🎉 Syntax is Valid! No indentation or structural YAML syntax errors found.")
                        st.info(f"**Detected Object Details:**\n* **API Version:** `{parsed_yaml.get('apiVersion', 'Not Specified')}`\n* **Kind:** `{parsed_yaml.get('kind', 'Not Specified')}`\n* **Name:** `{parsed_yaml.get('metadata', {}).get('name', 'Not Specified')}`")
                except yaml.YAMLError as exc:
                    st.error("❌ Syntax Error Found!")
                    st.code(str(exc), language="text")

    # tab 3: debug tab
    with tab3:
        st.subheader("Kubernetes Issue Log Debugger")
        error_input = st.text_area("Paste Error Logs here:", height=200)
        debug_btn = st.button("Analyze & Explain Error 🔍", type="primary")
        
        if debug_btn:
            if not error_input.strip():
                st.warning("Please paste an error log or code to diagnose.")
            else:
                with st.spinner("Gemini is diagnosing the root cause..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"Please analyze and provide a fix for this Kubernetes error:\n\n{error_input}",
                            config=types.GenerateContentConfig(system_instruction=K8S_DEBUG_PROMPT, temperature=0.2)
                        )
                        st.markdown(response.text)
                        
                        # 🟢 CREATE ACTION: Save to in-memory storage array
                        new_log = {
                            "id": str(uuid.uuid4()), # Generates a random ID
                            "icon": "🔍",
                            "title": f"Debug: {error_input[:20]}...",
                            "content": response.text,
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state["history_db"].append(new_log)
                        st.rerun()  
                        
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
