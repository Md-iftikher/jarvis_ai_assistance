import speech_recognition as sr
import pyttsx3
import webbrowser
import musicLibrary 
import os
from dotenv import load_dotenv 
import google.generativeai as genai

# Initialize recognizer and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit()
genai.configure(api_key=GEMINI_API_KEY)

available_models = [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]

if not available_models:
    print("Error: No Gemini models found that support text generation. Please check your API key and region.")
    exit()

preferred_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro", 
    "gemini-1.0-pro", 
]

selected_model_name = None
for p_model in preferred_models:
    for a_model in available_models:
        if p_model in a_model.name:
            selected_model_name = a_model.name
            break
    if selected_model_name:
        break

if not selected_model_name:
    
    selected_model_name = available_models[0].name
    print(f"Warning: No preferred model found. Using the first available model: {selected_model_name}")

print(f"Using Gemini model: {selected_model_name}")
model = genai.GenerativeModel(selected_model_name)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def ask_gemini(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Sorry, I couldn't process that request."


def process_command(command):
    command = command.lower().strip()

    # commands
    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open facebook" in command:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")
    elif "play" in command:
        try:
            song = command.split("play")[1].strip()
            if song in musicLibrary.music:
                link = musicLibrary.music[song]
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                speak(f"Sorry, I couldn't find {song} in my library")
        except Exception as e:
            print(f"Error playing song: {e}")
            speak("I couldn't play that song")
    elif "exit" in command or "quit" in command or "goodbye" in command:
        speak("Goodbye, Master!")
        exit()
    else:
        speak("Let me think about that...")
        response = ask_gemini(command)
        speak(response)

def listen_for_wake_word():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for wake word 'Jarvis'...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=3)
            try:
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                return "jarvis" in text
            except sr.UnknownValueError:
                print("Could not understand audio")
                return False
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return False
        except sr.WaitTimeoutError:
            print("No speech detected")
            return False

def listen_for_command():
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Command: {command}")
                return command
            except sr.UnknownValueError:
                speak("I didn't catch that. Could you repeat?")
                return None
            except sr.RequestError as e:
                speak("There was an error with the speech recognition service.")
                print(f"Error: {e}")
                return None
        except sr.WaitTimeoutError:
            print("No command detected")
            return None

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            if listen_for_wake_word():
                speak("Yes Master?")
                command = listen_for_command()
                if command:
                    process_command(command)
            else:
                print("Wake word not detected, listening again...")
                
        except KeyboardInterrupt:
            speak("Goodbye, Master!")
            exit()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            speak("Sorry, I encountered an error. Restarting...")