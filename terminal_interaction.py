import subprocess
import requests
import PyPDF2
#import speech_recognition as sr
from bs4 import BeautifulSoup
from io import BytesIO
import re
import pyttsx3

# URLs for updating the Flask server
HISTORY_URL = "http://127.0.0.1:5000/history"
MODE_URL = "http://127.0.0.1:5000/mode"

regular_history = []
rag_history = []
mode = "regular"

# Initialize TTS engine
engine = pyttsx3.init()

# Function to clean LLM output by removing special characters and control sequences
def clean_output(output):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    clean_text = ansi_escape.sub('', output)
    
    spinner_pattern = re.compile(r'[\u2800-\u28FF]+')
    clean_text = spinner_pattern.sub('', clean_text)
    
    clean_text = clean_text.replace('failed to get console mode for stdout: The handle is invalid.', '')
    clean_text = clean_text.replace('failed to get console mode for stderr: The handle is invalid.', '')
    
    return clean_text.strip()

# TTS function to speak the LLM response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# System prompts
regular_prompt = (
    "You are a helpful assistant working on social robotics. Please provide detailed, "
    "comprehensive responses to the user's queries based solely on the conversation history."
)
rag_prompt = (
    "You are an AI assistant with access to specific documents. Please provide thorough "
    "answers based on the document content provided, covering all relevant points in detail."
)

MODEL_NAME = "mistral"

# Function to interact with the LLM using the Ollama CLI for both modes
def chat_with_llm(prompt, model=MODEL_NAME):
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        output = result.stdout.strip()
        cleaned_output = clean_output(output)
        if result.returncode != 0:
            return f"Error: {cleaned_output}"
        return cleaned_output
    except Exception as e:
        return f"An error occurred: {str(e)}"

#RAG FUNCTIONALITY
# Function to load and extract text from a PDF using PyPDF2
def load_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
            return text
    except Exception as e:
        return f"An error occurred while reading the PDF: {str(e)}"

# Function to download and extract text from a PDF link
def download_and_extract_pdf(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with BytesIO(response.content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
            return text
    except Exception as e:
        return f"An error occurred while downloading the PDF: {str(e)}"

# Function to scrape and extract text from a webpage
def scrape_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(paragraph.get_text() for paragraph in paragraphs)
        return text
    except Exception as e:
        return f"An error occurred while scraping the webpage: {str(e)}"

# Function to handle RAG by combining the query with document content
def chat_with_rag(query, documents, model=MODEL_NAME):
    combined_input = rag_prompt + "\nUser Query: " + query + "\nDocument Content: " + documents
    response = chat_with_llm(combined_input, model=model)
    rag_history.append({"sender": "User", "text": query, "mode": mode})
    rag_history.append({"sender": "LLM (RAG)", "text": response, "mode": mode})
    update_conversation_history()
    speak(response)  # Speak the response
    return response

#REGULAR MODE
# Function to handle Regular conversation
def chat_with_regular(query, model=MODEL_NAME):
    combined_input = regular_prompt + "\nUser Query: " + query
    response = chat_with_llm(combined_input, model=model)
    regular_history.append({"sender": "User", "text": query, "mode": mode})
    regular_history.append({"sender": "LLM (Regular)", "text": response, "mode": mode})
    update_conversation_history()
    speak(response)  # Speak the response
    return response
'''
# Function to listen to voice input with confirmation and mode switching
def listen_to_voice():
    global mode
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            speak(f"Listening... (Current mode: {mode})")
            print(f"Listening... (Current mode: {mode})")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text} (Current mode: {mode})")
            if "switch to rag" in text:
                mode = "RAG"
                speak("Switched to RAG mode. (Current mode: RAG)")
                print("Switched to RAG mode. (Current mode: RAG)")
                update_mode()
                return None
            elif "switch to regular" in text:
                mode = "regular"
                speak("Switched to regular mode. (Current mode: regular)")
                print("Switched to regular mode. (Current mode: regular)")
                update_mode()
                return None

            speak(f"You said: {text}. Is this correct? Please say yes or no.")
            with sr.Microphone() as source:
                speak("Waiting for confirmation...")
                print("Waiting for confirmation...")
                confirmation_audio = recognizer.listen(source)
                confirmation = recognizer.recognize_google(confirmation_audio).lower()
                if confirmation == "yes":
                    speak("Processing your request.")
                    print("Processing your request.")
                    return text
                elif confirmation == "no":
                    speak("Let's try again.")
                    print("Let's try again.")
                else:
                    speak("Sorry, I didn't catch that. Please say yes or no.")
                    print("Sorry, I didn't catch that. Please say yes or no.")
        except sr.UnknownValueError:
            speak("Sorry, I could not understand your speech.")
            print("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            print(f"Could not request results; {e}")
            return None
'''

# WebUI Integration
#  Function to update the conversation history on the Flask server
def update_conversation_history():
    global mode
    try:
        if mode == 'regular':
            requests.post(HISTORY_URL, json=regular_history)
        elif mode == 'RAG':
            requests.post(HISTORY_URL, json=rag_history)
    except Exception as e:
        speak(f"Failed to update conversation history: {e}")
        print(f"Failed to update conversation history: {e}")

# Function to update the mode on the Flask server
def update_mode():
    try:
        requests.post(MODE_URL, json={'mode': mode})
    except Exception as e:
        speak(f"Failed to update mode: {e}")
        print(f"Failed to update mode: {e}")

def get_rag_input(user_input_mode):
    speak("Please provide the link (PDF or Webpage) for the document. (Current mode: RAG)")
    print("Please provide the link (PDF or Webpage) for the document. (Current mode: RAG)")
    
    url = input("Enter the link (PDF or Webpage) for RAG mode: ")
    if url.endswith('.pdf'):
        pdf_content = download_and_extract_pdf(url)
    else:
        pdf_content = scrape_webpage(url)

    if "An error occurred" in pdf_content:
        speak(pdf_content)
        print(pdf_content)
    else:
        speak("Thank you. Now, please provide your query. (Current mode: RAG)")
        print("Thank you. Now, please provide your query. (Current mode: RAG)")
        if user_input_mode == "voice":
            user_input = listen_to_voice()
        else:
            user_input = input("Enter your query: ")

        response = chat_with_rag(user_input, pdf_content)
        print(f"LLM (RAG): {response}")

#Mode switching and terminal input
def terminal_interface():
    global mode
    #speak(f"Starting LLM Chat. (Current mode: {mode}). Type switch to RAG to switch to RAG mode, switch to regular to switch back.")
    print(f"Starting LLM Chat. (Current mode: {mode}). Type 'switch to RAG' to switch to RAG mode, 'switch to regular' to switch back, or 'voice' to use voice input.")
    
    while True:
       # speak(f"Would you like to use text input or voice input? Please type 'text' or 'voice'. (Current mode: {mode})")
        user_input_mode = input(f"Enter 'text' for text input (Current mode: {mode}): ").strip().lower()
        
        if user_input_mode == "voice":
            user_input = listen_to_voice()
            if user_input is None:
                continue
        elif user_input_mode == "text":
            user_input = input(f"Enter your command or query. (Current mode: {mode}): ")
        else:
            #speak(f"Invalid option. Please choose 'text' or 'voice'. (Current mode: {mode})")
            print(f"Invalid option. Please choose 'text' or 'voice'. (Current mode: {mode})")
            continue

        # Custom response for "hey what's up!"
        if user_input.lower() == "hey what's up!":
            response = "not much just here to assist you"
            print(f"LLM: {response} (Current mode: {mode})")
           # speak(response)
            continue

        if user_input.lower() == "switch to rag":
            mode = "RAG"
            #speak("Switched to RAG mode. (Current mode: RAG)")
            print("Switched to RAG mode. (Current mode: RAG)")
            update_mode()
            get_rag_input(user_input_mode)
            continue

        elif user_input.lower() == "switch to regular":
            mode = "regular"
           # speak("Switched to regular mode. (Current mode: regular)")
            print("Switched to regular mode. (Current mode: regular)")
            update_mode()
            continue
        
        if mode == "regular":
            response = chat_with_regular(user_input)
            print(f"LLM (Regular): {response} (Current mode: regular)")
        elif mode == "RAG":
            get_rag_input(user_input_mode)

if __name__ == "__main__":
    terminal_interface()
