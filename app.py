import streamlit as st
from google import genai
from google.genai import types
import yaml

# initialize with gemini token
client = genai.Client(api_key="paste token")

# system promts: given to AI so it knows how to behave before we give instructions to it
# With those prompts the AI will not use conversational word but will go straight to point
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

# this is the prompt for the debug session in the browser
K8S_DEBUG_PROMPT = """
You are an expert Kubernetes troubleshooter. The user will provide an error log, a `kubectl` error statement, or a status description (like CrashLoopBackOff, ImagePullBackOff, CreateContainerConfigError).

Your job is to:
1. Briefly explain **why** this error happens in plain, clear language.
2. Provide a bulleted list of **actionable steps** to fix the issue.
3. If applicable, provide the exact `kubectl` troubleshooting commands they should run to investigate further (e.g., `kubectl describe pod ...`, `kubectl logs ...`).
Be direct, highly technical, and concise. Do not use conversational filler.
"""

# this configures browser tab metadata.
st.set_page_config(page_title="K8s AI Toolkit", page_icon="☸️", layout="wide")
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
        
        additional_details = st.text_area(
            "Additional Details / Custom Requests", 
            placeholder="e.g., 'I need 3 replicas, environment variables for DB_HOST, and a NodePort service type.'",
            key="gen_details"
        )
        
        generate_btn = st.button("Generate Manifest 🚀", type="primary")

    with col2:
        st.subheader("Generated Manifest & Suggestions")
        if generate_btn:
            # uses a prompt but with our indications about image, port, name and other requiremnts
            user_prompt = f"""
            Please create a Kubernetes {manifest_type} for an application named '{app_name}'.
            - Container Image: {image_name}
            - Container Port: {container_port}
            - Additional Requirements: {additional_details}
            """
            # send the prompt to gemini engine
            with st.spinner("Gemini is analyzing and generating manifests..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=K8S_GENERATE_PROMPT,
                            temperature=0.2,
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# tab 2: validate yaml
with tab2:
    st.subheader("Syntax & Structural Validator")
    st.write("Paste your raw YAML manifest below to check for structural formatting or indentation issues.")
    
    yaml_input = st.text_area("Paste YAML Manifest here:", height=300, placeholder="apiVersion: apps/v1\nkind: Deployment\n...")
    validate_btn = st.button("Validate YAML ✅", type="primary")
    
    if validate_btn:
        if not yaml_input.strip():
            st.warning("Please paste some YAML code first.")
        else:
            try:
                # Attempt to parse the text as valid YAML
                parsed_yaml = yaml.safe_load(yaml_input)
                
                # Check if it loaded an empty document or a string instead of a dictionary structure
                if parsed_yaml is None or not isinstance(parsed_yaml, dict):
                    st.error("❌ Invalid format: The input is not structured as a valid Kubernetes object mapping.")
                else:
                    st.success("🎉 Syntax is Valid! No indentation or structural YAML syntax errors found.")
                    
                    # Provide a quick high-level overview of what was parsed
                    st.info(f"**Detected Object Details:**\n* **API Version:** `{parsed_yaml.get('apiVersion', 'Not Specified')}`\n* **Kind:** `{parsed_yaml.get('kind', 'Not Specified')}`\n* **Name:** `{parsed_yaml.get('metadata', {}).get('name', 'Not Specified')}`")
            
            except yaml.YAMLError as exc:
                st.error("❌ Syntax Error Found!")
                # Extract and format the specific line/column issue from the parser exception
                st.code(str(exc), language="text")
                st.warning("Tip: Check your indentation spaces carefully. Kubernetes YAML requires strict space usage; tabs are not allowed.")

# tab 3: debug tab
with tab3:
    st.subheader("Kubernetes Issue Log Debugger")
    st.write("Paste your cryptic error output from `kubectl get events`, `kubectl logs`, or `kubectl describe` to get plain-text root cause analysis.")
    
    error_input = st.text_area(
        "Paste Error Logs / Description here:", 
        height=200, 
        placeholder="e.g., 'Warning  FailedScheduling  3m4s  default-scheduler  0/3 nodes are available: 3 Insufficient cpu.'\nOR\n'Back-off restarting failed container'"
    )
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
                        config=types.GenerateContentConfig(
                            system_instruction=K8S_DEBUG_PROMPT,
                            temperature=0.2,
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
