import os
import sys
import time
import json
import webbrowser
import subprocess
import urllib.parse

import speech_recognition as sr
import pyttsx3
import pyautogui
from AppOpener import open as open_app
import ollama


# ============================================================
# J 2.0 - PERSONAL DESKTOP AI ASSISTANT
# ============================================================

ASSISTANT_NAME = "J"
OLLAMA_MODEL = "llama3.2"

MEMORY_FILE = "j_memory.json"
SCREENSHOT_FOLDER = "J_Screenshots"


# ============================================================
# TEXT TO SPEECH
# ============================================================

try:
    engine = pyttsx3.init("sapi5")
except Exception:
    engine = pyttsx3.init()

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

if voices:
    engine.setProperty("voice", voices[1].id)


def speak_and_print(text):
    """Print and speak J's response."""

    print(f"\n{ASSISTANT_NAME}: {text}")

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.6
recognizer.phrase_threshold = 0.3


def setup_microphone():
    """Prepare microphone once instead of recalibrating every time."""

    try:
        with sr.Microphone() as source:
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print("Microphone ready.")

    except Exception as e:
        print(f"Microphone error: {e}")


def listen(timeout=5, phrase_time_limit=6):
    """Listen to microphone and convert speech to text."""

    try:

        with sr.Microphone() as source:

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        try:

            command = recognizer.recognize_google(audio)

            return command.lower().strip()

        except sr.UnknownValueError:
            return ""

        except sr.RequestError:
            return ""

    except sr.WaitTimeoutError:
        return ""

    except Exception as e:
        print(f"Listening error: {e}")
        return ""


# ============================================================
# MEMORY SYSTEM
# ============================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:
        return {}


def save_memory(memory):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4
            )

    except Exception as e:
        print(f"Memory error: {e}")


memory = load_memory()


# ============================================================
# CONVERSATION MEMORY
# ============================================================

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are J, an intelligent personal desktop AI assistant.

Your personality:
- Smart
- Friendly
- Natural
- Concise
- Helpful
- Slightly futuristic

You are running locally on the user's Windows computer.

Give answers that sound natural when spoken aloud.
Avoid unnecessary long explanations unless the user asks for detail.
"""
}


chat_history = [SYSTEM_PROMPT]


# ============================================================
# MEMORY COMMANDS
# ============================================================

def remember_information(command):

    lower = command.lower()

    triggers = [
        "remember that",
        "remember this",
        "save this",
        "don't forget that",
        "dont forget that"
    ]

    for trigger in triggers:

        if lower.startswith(trigger):

            information = command[len(trigger):].strip()

            if information:

                memory["user_memory"] = information

                save_memory(memory)

                speak_and_print(
                    "Got it. I'll remember that."
                )

                return True

    return False


def show_memory():

    if "user_memory" in memory:

        speak_and_print(
            f"I remember: {memory['user_memory']}"
        )

    else:

        speak_and_print(
            "I don't have anything saved yet."
        )


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(command):

    websites = {

        "youtube": "https://www.youtube.com",

        "google": "https://www.google.com",

        "gmail": "https://mail.google.com",

        "github": "https://github.com",

        "instagram": "https://www.instagram.com",

        "facebook": "https://www.facebook.com",

        "chatgpt": "https://chatgpt.com",

    }

    for name, url in websites.items():

        if f"open {name}" in command:

            speak_and_print(
                f"Opening {name}"
            )

            webbrowser.open(url)

            return True

    return False


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(command):

    if (
        "google search" in command
        or "search for" in command
        or "search google for" in command
    ):

        query = command

        query = query.replace(
            "google search",
            ""
        )

        query = query.replace(
            "search google for",
            ""
        )

        query = query.replace(
            "search for",
            ""
        )

        query = query.strip()

        if not query:
            return True

        speak_and_print(
            f"Searching Google for {query}"
        )

        encoded = urllib.parse.quote_plus(query)

        webbrowser.open(
            f"https://www.google.com/search?q={encoded}"
        )

        return True

    return False


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(command):

    if (
        "search youtube for" in command
        or "play on youtube" in command
        or "youtube search" in command
    ):

        query = command

        query = query.replace(
            "search youtube for",
            ""
        )

        query = query.replace(
            "play on youtube",
            ""
        )

        query = query.replace(
            "youtube search",
            ""
        )

        query = query.strip()

        if not query:
            return True

        speak_and_print(
            f"Searching YouTube for {query}"
        )

        encoded = urllib.parse.quote_plus(query)

        webbrowser.open(
            f"https://www.youtube.com/results?search_query={encoded}"
        )

        return True

    return False


# ============================================================
# VOLUME CONTROLS
# ============================================================

def volume_controls(command):

    if "mute" in command:

        pyautogui.press("volumemute")

        speak_and_print("Volume muted.")

        return True

    if (
        "volume up" in command
        or "increase volume" in command
        or "increase the volume" in command
    ):

        pyautogui.press(
            "volumeup",
            presses=5
        )

        speak_and_print(
            "Volume increased."
        )

        return True

    if (
        "volume down" in command
        or "decrease volume" in command
        or "decrease the volume" in command
    ):

        pyautogui.press(
            "volumedown",
            presses=5
        )

        speak_and_print(
            "Volume decreased."
        )

        return True

    return False


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    os.makedirs(
        SCREENSHOT_FOLDER,
        exist_ok=True
    )

    timestamp = time.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = os.path.join(
        SCREENSHOT_FOLDER,
        f"screenshot_{timestamp}.png"
    )

    pyautogui.screenshot(filename)

    speak_and_print(
        "Screenshot captured."
    )

    print(
        f"Saved to: {filename}"
    )


# ============================================================
# CREATE FOLDER
# ============================================================

def create_folder(command):

    trigger = "create folder"

    if trigger not in command:
        return False

    folder_name = command.split(
        trigger,
        1
    )[1].strip()

    if not folder_name:

        speak_and_print(
            "Please tell me the folder name."
        )

        return True

    try:

        os.makedirs(
            folder_name,
            exist_ok=True
        )

        speak_and_print(
            f"Folder {folder_name} created."
        )

    except Exception:

        speak_and_print(
            "I couldn't create that folder."
        )

    return True


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_application(command):

    if not command.startswith("open "):
        return False

    if any(
        word in command
        for word in [
            "browser",
            "website",
            "youtube",
            "google",
            "gmail",
            "github",
            "instagram",
            "facebook",
            "chatgpt"
        ]
    ):
        return False

    app_name = command.replace(
        "open",
        "",
        1
    ).strip()

    if not app_name:
        return False

    speak_and_print(
        f"Opening {app_name}"
    )

    try:

        open_app(
            app_name,
            match_closest=True,
            output=False
        )

        return True

    except Exception:

        speak_and_print(
            f"I couldn't find {app_name}."
        )

        return True


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application(command):

    if not command.startswith("close "):
        return False

    app_name = command.replace(
        "close",
        "",
        1
    ).strip()

    if not app_name:
        return False

    speak_and_print(
        f"Closing {app_name}"
    )

    try:

        subprocess.run(
            [
                "taskkill",
                "/IM",
                f"{app_name}.exe",
                "/F"
            ],
            capture_output=True
        )

    except Exception:

        speak_and_print(
            "I couldn't close that application."
        )

    return True


# ============================================================
# LOCK COMPUTER
# ============================================================

def lock_pc(command):

    if (
        "lock my pc" in command
        or "lock computer" in command
        or "lock my computer" in command
    ):

        speak_and_print(
            "Locking your computer."
        )

        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ]
        )

        return True

    return False


# ============================================================
# SLEEP COMPUTER
# ============================================================

def sleep_pc(command):

    if (
        "sleep my pc" in command
        or "sleep computer" in command
        or "put my pc to sleep" in command
    ):

        speak_and_print(
            "Putting the computer to sleep."
        )

        subprocess.run(
            [
                "rundll32.exe",
                "powrprof.dll,SetSuspendState",
                "0",
                "1",
                "0"
            ]
        )

        return True

    return False


# ============================================================
# SHUTDOWN / RESTART
# ============================================================

def power_controls(command):

    if (
        "shutdown"
        in command
        or "shut down"
        in command
    ):

        speak_and_print(
            "This will shut down the computer. "
            "Say yes to confirm."
        )

        confirmation = listen(
            timeout=5,
            phrase_time_limit=3
        )

        if confirmation in [
            "yes",
            "yes j",
            "confirm",
            "do it"
        ]:

            speak_and_print(
                "Shutting down."
            )

            subprocess.run(
                [
                    "shutdown",
                    "/s",
                    "/t",
                    "5"
                ]
            )

        else:

            speak_and_print(
                "Shutdown cancelled."
            )

        return True

    if (
        "restart"
        in command
        or "reboot"
        in command
    ):

        speak_and_print(
            "This will restart the computer. "
            "Say yes to confirm."
        )

        confirmation = listen(
            timeout=5,
            phrase_time_limit=3
        )

        if confirmation in [
            "yes",
            "yes j",
            "confirm",
            "do it"
        ]:

            speak_and_print(
                "Restarting."
            )

            subprocess.run(
                [
                    "shutdown",
                    "/r",
                    "/t",
                    "5"
                ]
            )

        else:

            speak_and_print(
                "Restart cancelled."
            )

        return True

    return False


# ============================================================
# SYSTEM TASK MANAGER
# ============================================================

def execute_system_task(command):

    # Memory
    if remember_information(command):
        return True

    if (
        "what do you remember"
        in command
        or "show my memory"
        in command
    ):

        show_memory()

        return True

    # Website
    if open_website(command):
        return True

    # Google
    if google_search(command):
        return True

    # YouTube
    if youtube_search(command):
        return True

    # Volume
    if volume_controls(command):
        return True

    # Screenshot
    if (
        "take screenshot" in command
        or "take a screenshot" in command
        or command == "screenshot"
    ):

        take_screenshot()

        return True

    # Folder
    if create_folder(command):
        return True

    # Close apps
    if close_application(command):
        return True

    # Open apps
    if open_application(command):
        return True

    # Lock
    if lock_pc(command):
        return True

    # Sleep
    if sleep_pc(command):
        return True

    # Shutdown / restart
    if power_controls(command):
        return True

    return False


# ============================================================
# LOCAL AI
# ============================================================

def ask_local_llm(prompt):

    global chat_history

    # Add saved memory to context
    memory_context = ""

    if "user_memory" in memory:

        memory_context = (
            "\nUseful information to remember about "
            f"the user: {memory['user_memory']}\n"
        )

    chat_history.append(
        {
            "role": "user",
            "content": prompt + memory_context
        }
    )

    # Keep conversation small and fast
    if len(chat_history) > 12:

        chat_history = (
            [SYSTEM_PROMPT]
            + chat_history[-11:]
        )

    try:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=chat_history
        )

        reply = response[
            "message"
        ][
            "content"
        ]

        chat_history.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        return reply

    except Exception as e:

        print(
            f"Ollama error: {e}"
        )

        return (
            "My local AI brain isn't responding. "
            "Please make sure Ollama is running."
        )


# ============================================================
# WAKE WORDS
# ============================================================

wake_triggers = [

    "hey j",
    "hey jay",
    "hey jae",

    "hi j",
    "hi jay",

    "hello j",
    "hello jay",

    "j assistant",
    "jay assistant",

    "hey jade",
    "hey jey",

    "hey joy",
    "hey joe",

    "hey gee",

    "hey day",

]


# ============================================================
# EXIT WORDS
# ============================================================

exit_triggers = [

    "goodbye j",
    "good bye j",

    "bye j",
    "stop j",
    "sleep j",

    "go to sleep",

    "exit j",

    "goodbye jay",
    "bye jay",
    "stop jay",
    "sleep jay",

    "goodbye gee",
    "bye gee",

]


# ============================================================
# CHECK WAKE WORD
# ============================================================

def is_wake_word(text):

    text = text.lower().strip()

    for trigger in wake_triggers:

        if trigger in text:
            return True

    # Standalone "j" / "jay"
    if text in [
        "j",
        "jay",
        "jae",
        "gee",
        "ji"
    ]:

        return True

    return False


# ============================================================
# ACTIVE SESSION
# ============================================================

def active_session():

    speak_and_print(
        "Yes, I am online. How can I help you?"
    )

    while True:

        print(
            "\n[J is Active... Listening]"
        )

        user_input = listen(
            timeout=5,
            phrase_time_limit=7
        )

        if not user_input:
            continue

        print(
            f"You: {user_input}"
        )

        # Exit active mode
        if any(
            trigger in user_input
            for trigger in exit_triggers
        ):

            speak_and_print(
                "Goodbye. Going back to standby."
            )

            break

        # System command
        if execute_system_task(
            user_input
        ):

            continue

        # AI
        reply = ask_local_llm(
            user_input
        )

        speak_and_print(
            reply
        )


# ============================================================
# STANDBY LOOP
# ============================================================

def main_standby_loop():

    print(
        "\n===================================="
    )

    print(
        "           J 2.0 ONLINE"
    )

    print(
        "===================================="
    )

    print(
        "\nJ is sleeping in background."
    )

    print(
        "Say 'Hey J' or 'Jay' to activate."
    )

    print(
        "Press CTRL+C to completely exit."
    )

    print(
        "====================================\n"
    )

    while True:

        try:

            text = listen(
                timeout=3,
                phrase_time_limit=4
            )

            if text:

                print(
                    f"(Standby heard: '{text}')"
                )

                if is_wake_word(text):

                    active_session()

            time.sleep(0.2)

        except KeyboardInterrupt:

            print(
                "\nJ shutting down..."
            )

            break

        except Exception as e:

            print(
                f"Standby error: {e}"
            )

            time.sleep(1)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    setup_microphone()

    main_standby_loop()