# JSB Interview Problem - LLM-RAG-WebUI Integration
## Author: Aastha Joshi
## Email: ajoshi8879@sdsu.edu

This project demonstrates the integration of a Large Language Model (LLM) for back-and-forth communication and Retrieval-Augmented Generation (RAG) functionality. The solution allows terminal-based input, mode switching, and WebUI display of interactions. It is designed to fulfill the problem statement requirements as outlined.

# Features
## Core Functionalities
### Back-and-Forth Communication:
Users interact with the LLM via terminal commands.
LLM responds conversationally based on the provided queries.

### Retrieval-Augmented Generation (RAG):
Users can provide links to PDFs or web articles for the LLM to retrieve relevant data and answer queries more comprehensively.

### Mode Switching:
Two modes: Regular Mode (conversation-based) and RAG Mode (document-based responses).
Users can switch between modes without restarting the program using terminal commands:
switch to rag to enable RAG mode.
switch to regular to return to Regular mode.

### WebUI Integration:
Displays conversation history in a chat-like format.
Differentiates between Regular and RAG mode using color-coded messages.
Auto-updates every 2 seconds to reflect terminal interactions.

## Setup Instructions
Prerequisites
Python Environment:
Use Python 3.8–3.10 (recommended: Python 3.8).
Create and activate a virtual environment using conda or venv.
Dependencies:
Install the required Python libraries
Ollama Setup: Install and configure Ollama CLI to run LLMs locally.
Download a small LLM (e.g., gemma:2b or tinyllama) for efficient processing.
Run Flask App:Navigate to the project folder and run the Flask server:
python app.py
How to Use
1. Run the Terminal Interaction Script
python terminal_interaction.py
2. Enter Commands in the Terminal
3. Interact with the WebUI
Open a browser and navigate to http://127.0.0.1:5000/.


