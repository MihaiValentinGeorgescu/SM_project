# ☸️ Kubernetes AI Developer Toolkit

## 📋 Project Description
The Kubernetes AI Developer Toolkit is a lightweight, AI-powered web dashboard designed to accelerate the creation, inspection, and troubleshooting of Kubernetes infrastructure manifests. Built entirely in Python using the Streamlit framework, this application streamlines the DevOps loop by offering a three-tier system:

1. **Manifest Generation:** Translates natural language requirements into optimized, production-ready YAML templates.
2. **YAML Validation:** A fast, local syntax checking engine to catch indentation and formatting mistakes before applying code to a cluster.
3. **Log Debugging:** Converts cryptic error signatures from production environments into step-by-step diagnostic solution workflows.

The application includes a built-in session authentication mechanism and a complete, in-memory CRUD backend layer that aggregates past code configurations and analytical outputs into an accessible sidebar history layout.

---

## ⚙️ Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8 or a newer version installed on your machine.

### 2. Install Project Dependencies
Run the following pip command in your terminal terminal to install the specific libraries required for formatting, UI, and model connectivity:
```bash
pip install streamlit google-genai pyyaml
