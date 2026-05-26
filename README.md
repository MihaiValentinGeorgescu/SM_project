## Kubernetes AI Developer Toolkit

### Project Description

This is a simple web app built with Python and Streamlit. It uses AI to help you work with Kubernetes. It does three main things:

Writes Code: You tell it what you want in plain English, and the AI writes the Kubernetes YAML code for you.

Checks Format: You paste your YAML code, and it checks if your spaces and format are correct (this is a syntax check).

Fixes Errors: You paste a messy Kubernetes error, and the AI tells you how to fix it in plain English.

The app also has a login screen and saves a history of the code you generate on the left side of the screen.

⚙️ Setup Instructions

1. What you need

Make sure you have Python installed on your computer.

2. Install required tools

Open your terminal and run this command to download the tools we need:
```
pip install streamlit google-genai pyyaml
```


3. Start the app

Go to the folder where your app.py file is and run:
```
streamlit run app.py
```

4. Login Details

When the app opens, it asks for a login. Use these details to get in:
```
Username: admin

Password: password123
```

### Technologies Used

Streamlit: Builds the web page, buttons, and text boxes using only Python. No HTML or JavaScript needed.

Google Gemini AI: The AI "brain" that writes your code and reads your errors.

PyYAML: A tool that reads your YAML code to see if you made any spacing mistakes.

UUID: A Python tool that gives a random, unique ID number to every file you save.

🔌 How the API Works

The app talks directly to Google's Gemini AI (gemini-2.5-flash).

Strict AI (Temperature = 0.2): We set the AI "temperature" very low. This stops the AI from being creative or guessing. It forces the AI to be strict and accurate, which is exactly what we want for coding.

Secret Rules (System Prompts): Before you even type a message, the app secretly tells the AI: "You are an expert. Only give me code. Do not say hello or use chatbot filler words."

### Database Structure & CRUD

The app does not use a heavy database like MySQL. Instead, it saves your data directly in the computer's temporary memory (RAM) using Streamlit's session_state.

Here is how the CRUD (Create, Read, Update, Delete) works:

Create: When the AI generates a good answer, the app packages that answer into a dictionary, gives it a unique ID, and saves it to a list in the memory.

Read: The app reads that list backwards and shows your saved files on the left sidebar (newest first).

Update: If you edit the text in the sidebar and click "Save", the app searches the list for that specific ID and updates the text.

Delete: If you click "Delete", the app finds that ID, removes it from the list entirely, and refreshes the screen.

### AI Features Explained

Code Generator: When you ask for an app, the AI doesn't just give you the bare minimum. It actively suggests best practices, like telling you to add memory limits or health checks so your app doesn't crash.

Error Troubleshooter: Terminal errors are hard to read. You paste them in, and the AI translates them. It tells you exactly why it broke and gives you the exact kubectl command to type next to fix it.

### How Embeddings/RAG Work (Future Plan)

Right now: The app just uses the AI's general knowledge. It does not read your private company files.

The Future (RAG): Later, we will add RAG (Retrieval-Augmented Generation). This means:

We will take your company's private rules (like allowed passwords or specific networks) and turn them into searchable data.

When you ask a question, the app will search those rules first.

It will give those rules to the AI, so the AI writes code that perfectly matches your company's security policies.

### API Limitations & Future Improvements

Current Weaknesses

Data Gets Wiped: Because we save data in temporary RAM memory, if you refresh the webpage, all your saved history disappears.

Unsafe Login: The admin password is hardcoded directly into the script. Anyone who reads the code can see it.

Format Check vs. Reality Check (Syntax vs Semantic): Our YAML checker only looks at spacing and colons (Syntax). It does not check if the app or secret you are trying to deploy actually exists in real life (Semantic).

What We Will Fix Next

Hide Passwords: Move the login details into a safe, hidden .env file.

Real Database: Connect a real database (like SQLite) so your history stays saved even if you close the browser.

Push to Kubernetes: Add a button that automatically deploys the generated code straight to your Kubernetes cluster so you don't have to copy and paste.
