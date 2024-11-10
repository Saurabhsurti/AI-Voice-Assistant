import os
# from pipes import quote
import pywhatkit
from urllib.parse import quote_plus
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import psutil   
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat
from plyer import notification
from pyautogui import click
from time import sleep
import wolframalpha
from translate import Translator
import PyPDF2
from gtts import gTTS
import math
import pyttsx3
import speech_recognition as sr

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()

def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return e
    
    return query.lower()


con = sqlite3.connect("robo.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong while connecting to database")

def closeCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("close", "")
    query = query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            # First, try to close any application from the sys_command table
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                app_path = results[0][0]
                app_executable = os.path.basename(app_path)

                # Attempt to close the application by killing the process
                if terminate_process(app_executable):
                    speak("Closing " + app_name)
                else:
                    speak(f"Couldn't close {app_name}. It might not be running.")

            elif len(results) == 0:
                # Try to close any website opened in a browser
                cursor.execute(
                    'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()

                if len(results) != 0:
                    speak(f"Cannot directly close {app_name} since it's a web page.")
                    # In case you want to close the browser itself:
                    # terminate_process('chrome') # Assuming Chrome is used for web browsing

                else:
                    # If the app is not found in the database, try closing it by its name directly
                    if terminate_process(app_name):
                        speak("Closing " + app_name)
                    else:
                        speak(f"Couldn't close {app_name}. It might not be running.")
        except:
            speak("Something went wrong while connecting to the database")


def terminate_process(process_name):
    """
    Function to terminate a process by its name.
    Returns True if the process was found and terminated, False otherwise.
    """
    found = False
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                proc.terminate()
                found = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return found

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:  # Check if search_term is not None
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't understand the song name.")


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video','whatsapp','please','plz','can','you','?','can','you','tu']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        robo_message = "message send successfully to "+name
        
    elif flag == 'call':
        target_tab = 7
        message = ''
        robo_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        robo_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote_plus(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(robo_message)

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'C:\\Users\\saura\\Downloads\\platform-tools-latest-windows\\platform-tools\\adb.exe shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(370, 2563)
    #start chat
    tapEvents(1052, 2578)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(705, 636)
    # tap on input
    tapEvents(560, 2665)
    #message
    adbInput(message)
    #send
    tapEvents(1094, 1660)
    speak("message send successfully to "+name)

def TimeTable1():
    speak("Checking....")

    from engine.timetable.TimeTable import Time

    value = Time()

    notification.notify(
        title="TimeTable",
        message=str(value),
        app_name="Robo",  # Customize this if needed
    )

    speak("AnyThing Else Sir ??")

def OnlinClass(Subject):

    if 'science' in Subject:

        from engine.OnlineClasses.Links import Science

        Link = Science()

        webbrowser.open(Link)

        sleep(10)

        click(x=629, y=788)

        sleep(1)

        click(x=1354, y=598)

        speak("Class Joined Sir .")

    elif 'mathematics' in Subject:

        from engine.OnlineClasses.Links import Maths

        Link = Maths()

        webbrowser.open(Link)

        sleep(10)

        click(x=629, y=788)

        sleep(1)

        click(x=1354, y=598)

        speak("Class Joined Sir .")

    elif 'social' in Subject:

        from engine.OnlineClasses.Links import sst

        Link = sst()

        webbrowser.open(Link)

        sleep(10)

        click(x=629, y=788)

        sleep(1)

        click(x=1354, y=598)

        speak("Class Joined Sir .")

    elif 'hindi' in Subject:

        from engine.OnlineClasses.Links import Hindi

        Link = Hindi()

        webbrowser.open(Link)

        sleep(10)

        click(x=629, y=788)

        sleep(1)

        click(x=1354, y=598)

        speak("Class Joined Sir .")

    elif 'english' in Subject:

        from engine.OnlineClasses.Links import English

        Link = English()

        webbrowser.open(Link)

        sleep(10)

        click(x=629, y=788)

        sleep(1)

        click(x=1354, y=598)

        speak("Class Joined Sir .")

def WolfRam(q):
    # api_key = os.getenv('API')
    api_key = "7HHXXP-XU5WLXQHXA"
    requester = wolframalpha.Client(api_key)
    requested = requester.query(q)
    try:
        Answer = next(requested.results).text 
        return Answer
    except:
        speak("An String Value is Not Answerable!!")

@eel.expose
def Temperature(q):
    temp = str(q)
    temp = temp.replace("robo","")
    temp = temp.replace("in","")
    temp = temp.replace("what is the","")
    temp = temp.replace("temperature","")

    temp_query = str(temp)

    if 'outside' in temp_query:
        var1="Temperature in Ahmedabad"
        answer = WolfRam(var1)
        speak(f"The Temperature Outside is {answer}")
    else:
        var2 = "Temperature in " + temp_query
        answer = WolfRam(var2)
        speak(f"{var2} is {answer}")

@eel.expose
def Music(musicName):
    if 'chale aana' in musicName:
        os.startfile("C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Sound\\chale aana.mp3")
    elif 'humnava mere' in musicName:
        os.startfile("C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Sound\\Humnava Mere.mp3")
    elif 'bulleya' in musicName:
        os.startfile("C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Sound\\Bulleya.mp3")
    else:
        pywhatkit.playonyt(musicName)
    
    speak("Your Song has been started!, Enjoy Sir!")

def Reader():
    speak("Tell Me the Name of the Book")

    name=takecommand()

    if 'india' in name:
        os.startfile("C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Books\\ch1.pdf")
        book=open("C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Books\\ch1.pdf", 'rb')
        pdfreader1 = PyPDF2.PdfReader(book)
        pages = len(pdfreader1.pages)
        speak(f"Number of Pages in This Books Are {pages}")
        # speak("From which Page I Have to Start Reading?")
        # numPage=int(input("Enter the page Number: "))
        page = pdfreader1.pages[0]
        text=page.extract_text()
        speak("In Which language, I Have To Read?")
        lang = takecommand()

        if 'hindi' in lang:
            trans1 = Translator(to_lang='hi')  # Pass the target language 'hi' here
            chunk_size = 400  # Adjust the chunk size as needed
            num_chunks = math.ceil(len(text) / chunk_size)
            
            for i in range(num_chunks):
                chunk = text[i * chunk_size: (i + 1) * chunk_size]
                textHin = trans1.translate(chunk)
                textm = textHin

                try:
                    speech = gTTS(text=textm, lang="hi")
                    chunk_path = f"C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Books\\chunk_{i}.mp3"
                    speech.save(chunk_path)
                    playsound(chunk_path)
                    os.remove(chunk_path)  # Delete the chunk file after playing
                except Exception as e:
                    print("Error playing audio:", str(e))

        if 'english' in lang:
            trans1 = Translator(to_lang='en')  # Pass the target language 'hi' here
            chunk_size = 400  # Adjust the chunk size as needed
            num_chunks = math.ceil(len(text) / chunk_size)
            
            for i in range(num_chunks):
                chunk = text[i * chunk_size: (i + 1) * chunk_size]
                textHin = trans1.translate(chunk)
                textm = textHin

                try:
                    speech = gTTS(text=textm, lang="en")
                    chunk_path = f"C:\\Users\\saura\\OneDrive\\Documents\\Python-p\\Database\\Books\\chunk_{i}.mp3"
                    speech.save(chunk_path)
                    playsound(chunk_path)
                    os.remove(chunk_path)  # Delete the chunk file after playing
                except Exception as e:
                    print("Error playing audio:", str(e))
