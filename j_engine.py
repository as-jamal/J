import os
import json
import time
import subprocess
import webbrowser
import urllib.parse
import threading

import speech_recognition as sr
import pyttsx3
import pyautogui
import psutil

from AppOpener import open as open_app
import ollama


# ============================================================
# J CONFIGURATION
# ============================================================

ASSISTANT_NAME = "J"
OLLAMA_MODEL = "llama3.2"
MEMORY_FILE = "j_memory.json"
SCREENSHOT_FOLDER = "J_Screenshots"


# ============================================================
# TEXT TO SPEECH
# ============================================================

tts_lock = threading.Lock()
engine = None


def create_tts_engine():
    """
    Creates a fresh Windows SAPI5 TTS engine.
    """
    global engine

    try:
        new_engine = pyttsx3.init("sapi5")

    except Exception:
        try:
            new_engine = pyttsx3.init()
        except Exception as e:
            print("TTS initialization failed:", e)
            return False

    try:
        new_engine.setProperty("rate", 170)
        new_engine.setProperty("volume", 1.0)

        voices = new_engine.getProperty("voices")

        if voices:
            new_engine.setProperty("voice", voices[0].id)

        engine = new_engine
        return True

    except Exception as e:
        print("TTS configuration error:", e)
        return False


# Initialize TTS
create_tts_engine()


def speak(text):
    """
    Reliable TTS function.

    If SAPI5 fails, J automatically recreates
    the TTS engine and tries once more.
    """

    global engine

    if not text:
        return

    text = str(text).strip()

    if not text:
        return

    with tts_lock:

        # First attempt
        try:

            if engine is None:
                create_tts_engine()

            if engine is not None:

                # Clear anything left in the queue
                try:
                    engine.stop()
                except Exception:
                    pass

                engine.say(text)
                engine.runAndWait()

                return

        except Exception as e:

            print("\n========== TTS ERROR ==========")
            print(type(e).__name__)
            print(e)
            print("Restarting speech engine...")
            print("================================\n")

        # ----------------------------------------------------
        # RECOVERY ATTEMPT
        # ----------------------------------------------------

        try:

            engine = None

            time.sleep(0.2)

            if create_tts_engine():

                engine.stop()
                engine.say(text)
                engine.runAndWait()

                print("TTS recovered successfully.")

        except Exception as e:

            print("\n========== TTS RECOVERY FAILED ==========")
            print(type(e).__name__)
            print(e)
            print("=========================================\n")


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 250
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.5

microphone = None


def calibrate_microphone():

    global microphone

    try:

        microphone = sr.Microphone()

        print("\nCalibrating microphone...")

        with microphone as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print("Microphone ready.")
        print(
            "Energy threshold:",
            recognizer.energy_threshold
        )

        return True

    except Exception as e:

        print("\n========== MICROPHONE ERROR ==========")
        print(type(e).__name__)
        print(e)
        print("======================================\n")

        microphone = None

        return False


def listen(timeout=5, phrase_time_limit=7):

    global microphone

    if microphone is None:

        if not calibrate_microphone():

            return ""

    try:

        print("🎙 Listening...")

        with microphone as source:

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        print("🔎 Recognizing...")

        try:

            command = recognizer.recognize_google(audio)

            print("Recognized:", command)

            return command.lower().strip()

        except sr.UnknownValueError:

            print("❌ I couldn't understand the audio.")

            return ""

        except sr.RequestError as e:

            print(
                "❌ Speech recognition service error:",
                e
            )

            return ""

    except sr.WaitTimeoutError:

        print("⌛ Listening timed out.")

        return ""

    except Exception as e:

        print("\n========== LISTEN ERROR ==========")
        print(type(e).__name__)
        print(e)
        print("==================================\n")

        return ""


# ============================================================
# MEMORY
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


def save_memory(memory_data):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory_data,
                file,
                indent=4
            )

    except Exception as e:

        print("Memory error:", e)


memory = load_memory()


# ============================================================
# OLLAMA AI
# ============================================================

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are J, a smart personal desktop AI assistant.

Personality:
- Intelligent
- Friendly
- Natural
- Slightly futuristic
- Helpful
- Concise

You are running locally on a Windows computer.

Your responses will usually be spoken aloud,
so keep normal responses reasonably short
and natural.

If the user asks for detailed information,
you can provide a longer explanation.

Do not unnecessarily repeat the user's question.
"""
}


chat_history = [SYSTEM_PROMPT]


def ask_ai(prompt):

    global chat_history

    memory_text = ""

    if "user_memory" in memory:

        memory_text = (
            "\nUseful information about the user: "
            + memory["user_memory"]
        )

    chat_history.append(
        {
            "role": "user",
            "content": prompt + memory_text
        }
    )

    # Keep conversation from becoming too large
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

        reply = response["message"]["content"]

        chat_history.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        return reply

    except Exception as e:

        print("\n========== OLLAMA ERROR ==========")
        print(type(e).__name__)
        print(e)
        print("==================================\n")

        return (
            "I can't connect to my local AI brain right now. "
            "Please make sure Ollama is running."
        )


# ============================================================
# MEMORY COMMANDS
# ============================================================

def remember(command):

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

            info = command[len(trigger):].strip()

            if info:

                memory["user_memory"] = info

                save_memory(memory)

                return True, (
                    "Got it. I'll remember that."
                )

    return False, None


def get_memory(command):

    if (
        "what do you remember" in command
        or "show my memory" in command
    ):

        if "user_memory" in memory:

            return True, (
                "I remember: "
                + memory["user_memory"]
            )

        return True, (
            "I don't have anything saved yet."
        )

    return False, None


# ============================================================
# WEBSITES
# ============================================================

WEBSITES = {

    "youtube":
        "https://www.youtube.com",

    "google":
        "https://www.google.com",

    "gmail":
        "https://mail.google.com",

    "github":
        "https://github.com",

    "instagram":
        "https://www.instagram.com",

    "facebook":
        "https://www.facebook.com",

    "chatgpt":
        "https://chatgpt.com"
}


def open_website(command):

    for name, url in WEBSITES.items():

        if command == f"open {name}":

            webbrowser.open(url)

            return True, (
                f"Opening {name}."
            )

    return False, None


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(command):

    triggers = [
        "google search",
        "search for",
        "search google for"
    ]

    for trigger in triggers:

        if command.startswith(trigger):

            query = command[
                len(trigger):
            ].strip()

            if not query:

                return True, (
                    "What should I search for?"
                )

            encoded = urllib.parse.quote_plus(
                query
            )

            webbrowser.open(
                "https://www.google.com/search?q="
                + encoded
            )

            return True, (
                f"Searching Google for {query}."
            )

    return False, None


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(command):

    triggers = [
        "search youtube for",
        "play on youtube",
        "youtube search"
    ]

    for trigger in triggers:

        if command.startswith(trigger):

            query = command[
                len(trigger):
            ].strip()

            if not query:

                return True, (
                    "What should I search for?"
                )

            encoded = urllib.parse.quote_plus(
                query
            )

            webbrowser.open(
                "https://www.youtube.com/results?search_query="
                + encoded
            )

            return True, (
                f"Searching YouTube for {query}."
            )

    return False, None


# ============================================================
# VOLUME CONTROL
# ============================================================

def volume_control(command):

    if (
        command == "mute"
        or command == "mute volume"
    ):

        pyautogui.press("volumemute")

        return True, "Volume muted."

    if (
        "volume up" in command
        or "increase volume" in command
        or "increase the volume" in command
    ):

        pyautogui.press(
            "volumeup",
            presses=5
        )

        return True, "Volume increased."

    if (
        "volume down" in command
        or "decrease volume" in command
        or "decrease the volume" in command
    ):

        pyautogui.press(
            "volumedown",
            presses=5
        )

        return True, "Volume decreased."

    return False, None


# ============================================================
# SCREENSHOT
# ============================================================

def screenshot(command):

    if "screenshot" not in command:

        return False, None

    os.makedirs(
        SCREENSHOT_FOLDER,
        exist_ok=True
    )

    timestamp = time.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    path = os.path.join(
        SCREENSHOT_FOLDER,
        f"screenshot_{timestamp}.png"
    )

    try:

        pyautogui.screenshot(path)

        return True, (
            "Screenshot captured and saved."
        )

    except Exception:

        return True, (
            "I couldn't capture the screenshot."
        )


# ============================================================
# CREATE FOLDER
# ============================================================

def create_folder(command):

    trigger = "create folder"

    if not command.startswith(trigger):

        return False, None

    name = command[
        len(trigger):
    ].strip()

    if not name:

        return True, (
            "Please tell me the folder name."
        )

    try:

        os.makedirs(
            name,
            exist_ok=True
        )

        return True, (
            f"Folder {name} created."
        )

    except Exception:

        return True, (
            "I couldn't create that folder."
        )


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_application(command):

    if not command.startswith("open "):

        return False, None

    name = command[
        len("open "):
    ].strip()

    if not name:

        return False, None

    if name in WEBSITES:

        return False, None

    try:

        open_app(
            name,
            match_closest=True,
            output=False
        )

        return True, (
            f"Opening {name}."
        )

    except Exception:

        return True, (
            f"I couldn't find {name}."
        )


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application(command):

    if not command.startswith("close "):

        return False, None

    name = command[
        len("close "):
    ].strip()

    if not name:

        return False, None

    try:

        subprocess.run(
            [
                "taskkill",
                "/IM",
                f"{name}.exe",
                "/F"
            ],
            capture_output=True
        )

        return True, (
            f"Closing {name}."
        )

    except Exception:

        return True, (
            f"I couldn't close {name}."
        )


# ============================================================
# LOCK COMPUTER
# ============================================================

def lock_pc(command):

    if (
        "lock my pc" in command
        or "lock computer" in command
        or "lock my computer" in command
    ):

        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ]
        )

        return True, (
            "Locking your computer."
        )

    return False, None


# ============================================================
# SLEEP COMPUTER
# ============================================================

def sleep_pc(command):

    if (
        "sleep my pc" in command
        or "sleep computer" in command
        or "put my pc to sleep" in command
    ):

        subprocess.run(
            [
                "rundll32.exe",
                "powrprof.dll,SetSuspendState",
                "0",
                "1",
                "0"
            ]
        )

        return True, (
            "Putting the computer to sleep."
        )

    return False, None


# ============================================================
# SHUTDOWN / RESTART
# ============================================================

def power_control(command):

    if (
        "shutdown" in command
        or "shut down" in command
    ):

        return True, (
            "Shutdown command received. "
            "Please confirm before executing."
        )

    if (
        "restart" in command
        or "reboot" in command
    ):

        return True, (
            "Restart command received. "
            "Please confirm before executing."
        )

    return False, None


# ============================================================
# SYSTEM STATUS
# ============================================================

def system_status(command):

    # CPU
    if (
        "cpu usage" in command
        or "cpu status" in command
        or "how much cpu" in command
        or "cpu utilization" in command
    ):

        cpu = psutil.cpu_percent(
            interval=1
        )

        return True, (
            f"CPU usage is currently "
            f"{cpu:.0f} percent."
        )

    # RAM
    if (
        "ram usage" in command
        or "memory usage" in command
        or "how much ram" in command
        or "ram status" in command
    ):

        ram = psutil.virtual_memory()

        used = ram.used / (
            1024 ** 3
        )

        total = ram.total / (
            1024 ** 3
        )

        percentage = ram.percent

        return True, (
            f"You are using "
            f"{used:.1f} gigabytes of RAM "
            f"out of {total:.1f} gigabytes, "
            f"which is {percentage:.0f} percent."
        )

    # STORAGE
    if (
        "storage" in command
        or "disk space" in command
        or "free space" in command
        or "hard drive" in command
    ):

        try:

            disk = psutil.disk_usage(
                os.path.abspath(os.sep)
            )

            free = disk.free / (
                1024 ** 3
            )

            total = disk.total / (
                1024 ** 3
            )

            return True, (
                f"You have {free:.1f} gigabytes "
                f"of free storage out of "
                f"{total:.1f} gigabytes. "
                f"Storage usage is "
                f"{disk.percent:.0f} percent."
            )

        except Exception:

            return True, (
                "I couldn't check your storage."
            )

    # BATTERY
    if (
        "battery" in command
        or "battery level" in command
        or "battery status" in command
    ):

        try:

            battery = psutil.sensors_battery()

            if battery is None:

                return True, (
                    "I couldn't detect a battery."
                )

            percentage = battery.percent

            if battery.power_plugged:

                status = (
                    "and the charger is connected."
                )

            else:

                status = (
                    "and the charger is disconnected."
                )

            return True, (
                f"Battery is at "
                f"{percentage:.0f} percent "
                f"{status}"
            )

        except Exception:

            return True, (
                "I couldn't check the battery."
            )

    # NETWORK
    if (
        "internet" in command
        or "network" in command
        or "wifi" in command
        or "wi-fi" in command
    ):

        try:

            interfaces = psutil.net_if_stats()

            connected = any(
                info.isup
                for info in interfaces.values()
            )

            if connected:

                return True, (
                    "Your computer appears to "
                    "be connected to a network."
                )

            return True, (
                "I don't detect an active "
                "network connection."
            )

        except Exception:

            return True, (
                "I couldn't check the network."
            )

    return False, None


# ============================================================
# COMPLETE COMMAND PROCESSOR
# ============================================================

def process_command(command):

    command = command.lower().strip()

    if not command:

        return "I didn't hear anything."

    # MEMORY
    handled, response = remember(command)

    if handled:
        return response

    handled, response = get_memory(command)

    if handled:
        return response

    # WEBSITES
    handled, response = open_website(command)

    if handled:
        return response

    # GOOGLE
    handled, response = google_search(command)

    if handled:
        return response

    # YOUTUBE
    handled, response = youtube_search(command)

    if handled:
        return response

    # VOLUME
    handled, response = volume_control(command)

    if handled:
        return response

    # SCREENSHOT
    handled, response = screenshot(command)

    if handled:
        return response

    # FOLDER
    handled, response = create_folder(command)

    if handled:
        return response

    # CLOSE APP
    handled, response = close_application(command)

    if handled:
        return response

    # OPEN APP
    handled, response = open_application(command)

    if handled:
        return response

    # LOCK
    handled, response = lock_pc(command)

    if handled:
        return response

    # SLEEP
    handled, response = sleep_pc(command)

    if handled:
        return response

    # POWER
    handled, response = power_control(command)

    if handled:
        return response

    # SYSTEM STATUS
    handled, response = system_status(command)

    if handled:
        return response

    # ========================================================
    # EVERYTHING ELSE → OLLAMA
    # ========================================================

    return ask_ai(command)