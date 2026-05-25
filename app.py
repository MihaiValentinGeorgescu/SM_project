import streamlit as st
from google import genai
from google.genai import types

# Initialize the Gemini Client
# It will look for an environment variable named GEMINI_API_KEY, 
# or you can pass it directly if you put it in your secrets.toml
client = genai.Client(api_key="AIzaSyDnDkMUqtxegKKm_bQOIKg38axir2h_gjs")
# if you see this change this api token plssssss :D

# The Specialized Kubernetes Prompt
K8S_SYSTEM_PROMPT = """
You are an expert Kubernetes Platform Engineer and DevOps assistant. 
Your job is to generate highly optimized, secure, and production-ready Kubernetes manifests based on user requests.

Rules:
1. Return the valid YAML manifest inside a standard markdown code block.
2. After the YAML block, provide a section called "🛠️ Suggested Improvements & Best Practices".
3. In the improvements section, suggest cloud-native best practices specific to their request (e.g., adding resource limits, liveness/readiness probes, securityContext, network policies, or labels).
4. If the user's request lacks critical production pieces (like missing ports or image tags), infer smart defaults but highlight them in your suggestions.
5. Do not include long conversational fluff. Be direct and technical.
"""

st.set_page_config(page_title="K8s AI Assistant", page_icon="☸️", layout="wide")
st.title("☸️ Kubernetes AI Manifest Assistant (Powered by Gemini)")
st.caption("Tell the AI what you want to deploy, and it will generate the YAML and suggest best-practice improvements.")

# UI Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Describe Your Deployment")
    manifest_type = st.selectbox("What are we building?", ["Deployment + Service", "Deployment Only", "StatefulSet", "ConfigMap/Secret", "Ingress"])
    
    app_name = st.text_input("Application Name", value="my-web-app")
    image_name = st.text_input("Container Image", value="nginx:latest")
    container_port = st.number_input("Container Port", value=80)
    
    additional_details = st.text_area(
        "Additional Details / Custom Requests", 
        placeholder="e.g., 'I need 3 replicas, environment variables for DB_HOST, and a NodePort service type.'"
    )
    
    generate_btn = st.button("Generate Manifest 🚀", type="primary")

with col2:
    st.subheader("Generated Manifest & Suggestions")
    
    if generate_btn:
        user_prompt = f"""
        Please create a Kubernetes {manifest_type} for an application named '{app_name}'.
        - Container Image: {image_name}
        - Container Port: {container_port}
        - Additional Requirements: {additional_details}
        """
        
        with st.spinner("Gemini is analyzing and generating manifests..."):
            try:
                # Call the Gemini API with system instructions
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=K8S_SYSTEM_PROMPT,
                        temperature=0.2, # Low temperature for accurate code generation
                    )
                )
                
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
