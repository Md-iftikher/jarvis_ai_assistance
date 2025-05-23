import speech_recognition as sr
import pyttsx3
import webbrowser
import musicLibrary
from openai import OpenAI
import os
from .env import load_dotenv

# Initialize recognizer and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Load OpenAI API key from environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def speak(text):
    engine.say(text)
    engine.runAndWait()

def ask_openai(question):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Sorry, I couldn't process that request"

def process_Command(c):
    c = c.lower().strip()
    
    # Existing commands
    if "open google" in c or "google" in c:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c or "facebook" in c:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in c or "youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open linkedin" in c or "linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")
    elif "play" in c:
        try:
            song = c.split("play")[1].strip()
            if song in musicLibrary.music:
                link = musicLibrary.music[song]
                speak(f"Playing {song}")
                webbrowser.open(link)
            else:
                speak(f"Sorry, I couldn't find {song} in my library")
        except Exception as e:
            print(f"Error: {e}")
            speak("I couldn't play that song")
    else:
        # Handle all other queries with OpenAI
        speak("Let me think about that...")
        response = ask_openai(c)
        speak(response)

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
                word = recognizer.recognize_google(audio).lower()
                print("You said:", word)
                
                if word == "jarvis":
                    speak("Yes Master?")
                    
                    with sr.Microphone() as source:
                        print("Listening for command...")
                        audio = recognizer.listen(source)
                        command = recognizer.recognize_google(audio)
                        print("Command:", command)
                        process_Command(command)
                        
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Error: {e}")