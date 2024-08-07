"""
This is a voice assistant project created by Anna Mityukova.

For the use of the weather prediction and opening music from spotify it is necessary to create additional keys.
For the weather I used key from the website https://openweathermap.org/
For the music I used spotify developer account

In order to implement NLU I used hugging face transformers, created a custom dataset and trained the model on
Google Colab.

Commands for the installing additional libraries:

pip install transformers
pip install pyttsx3
pip install speech_recognition
pip install termcolour
pip install spotipy
pip install wikipedia
pip install pyjokes

for a quick installation it could be useful to run:
pip install requirements.txt

"""

from transformers import pipeline
import pyttsx3
import random
import speech_recognition
from termcolor import colored
import os
import requests
import time
import spotipy
import webbrowser
import wikipedia
from pyjokes import get_joke
import re


class VoiceAssistant:
    """
    Settings for the voice assistant including name and sex
    """
    name = ""
    sex = ""


def setup_assistant_voice():
    """
    Setting up the voice of the assistant based on its sex (Microsoft Zira Desktop if sex is "female" and Microsoft
    David Desktop if sex is "male")
    """
    if assistant.sex == "female":
        en_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        ttsEngine.setProperty('voice', en_voice_id)
    if assistant.sex == "male":
        ttsEngine.setProperty("voice", 'en_us')


def play_assistant_speech(text):
    """
    This function is used to produce speech of the voice assistant
    """
    ttsEngine.say(str(text))
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):
    """
    This function makes it possible to listen to user and use online recognition to transform speech to text.
    It takes the user voice as input and returns the text converted from speech
    """
    with microphone:
        recognized_data = ""

        # background noise regulation
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        # online-recognition
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="en").lower()

        except speech_recognition.UnknownValueError:
            pass

        # catching problem
        except speech_recognition.RequestError:
            print("Check your Internet Connection, please")

        return recognized_data


def get_label(BERT_classifier, raw_text):
    """
    This function takes the fine-tuned model and the text to classify the intent of the prompt
    """
    command = BERT_classifier(raw_text)[0]['label']
    return command

def play_greetings():
    """
    This function uses the combination of several greeting phrases to say hello to the user
    """

    # list of greetings
    greetings = ["Hello. ", "Hi. ", "Good afternoon. ", "Hello, human. "]

    # list of phrases for better user interaction
    ask_for_help_phrases = ["How can I help you?", "Can I help you", "How can I be useful today?",
                            "Do you need any help?"]

    # choosing one greeting and one help phrase from the lists and combine them:
    greeting = greetings[random.randint(0, len(greetings) - 1)]
    ask_for_help = ask_for_help_phrases[random.randint(0, len(ask_for_help_phrases) - 1)]
    phrase = greeting + ask_for_help

    # converting text to speech:
    play_assistant_speech(phrase)


def play_farewells_and_quit():
    """
    This function is saying goodbye to the user and stops running the program
    """
    # list of farewells
    farewells = ["Bye. ", "I was happy to help", "Thank you, bye", "Goodbye", "Cheers!", "See you later!"]

    # playing a random farewell to the user
    play_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])

    # stopping to convert text to speech
    ttsEngine.stop()

    # stopping the program
    quit()


def play_failure_phrases():
    """
    This function is used to ask user to repeat their prompt again in case if the model failed to classify it.
    """
    # list of phrases
    failure_phrases = ["I am sorry, I cannot understand you. What did you ask? ",
                       "Sorry, could you please repeat this again?",
                       "Excuse me, can you repeat it please?"]

    # converting text to speech
    play_assistant_speech(failure_phrases[random.randint(0, len(failure_phrases) - 1)])


def weather_preparation():
    """
    This function prepares the required data for telling the current weather and make a weather forecast.

    To work with the weather data I used resource: https://openweathermap.org/
    To create an API key it is needed to register on this cite and generate a key.
    The key I saved in the file called 'weather_api_key'
    """
    with open("weather_api_key", 'r') as file:
        api_key = str(file.read())
        file.close()

    # latitude and longitude of the city where the owner of the voice assistant lives
    # These values should be stated because the free subscription plan on the openweathermap.org
    # limits the opportunities
    lat = 53.381130
    lon = -1.470085

    return api_key, lat, lon


def get_current_weather(api_key, lat, lon):
    """
    This function uses api key to access the openweathermap.org, this data is then used to return the current weather
    in the specific city
    """
    response = requests.get(
        # getting the data and setting units to metric. Without specifying units, the weather will be in Kelvin
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric')
    weather_data = response.json()

    # Obtaining information about the weather state, temperature, how the temperature feels like, humidity and
    # wind speed at the current moment.
    observed_weather = (weather_data['weather'][0])['main']
    current_temp = int(weather_data['main']['temp'])
    current_temp_feels_like = int(weather_data['main']['feels_like'])
    current_humidity = weather_data['main']['humidity']
    current_wind_speed = weather_data['wind']['speed']

    # transforming text to speech
    play_assistant_speech(f"The weather now can be described as {observed_weather}, current temperature is {current_temp} "
                       f"degrees Celsius, however it feels like the temperature is {current_temp_feels_like} degrees."
                       f"The humidity is {current_humidity} and the wind speed is about {current_wind_speed} meters per second")


def get_weather_forecast(api_key, lat, lon):
    """
    This function gets the data from openweathermap.org. It allows to make a weather prediction for the next 3
    and 6 hours
    """
    # getting the data
    response = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric')
    weather_forecast_data = response.json()

    # getting the prediction for the weather and temperature for the next 3 hours
    predicted_weather_in_3_hrs = weather_forecast_data['list'][1]['weather'][0]['description']
    predicted_temperature_in_3_hrs = weather_forecast_data['list'][1]['main']['temp']

    # getting the prediction for the weather and temperature for the next 6 hours
    predicted_weather_in_6_hrs = weather_forecast_data['list'][2]['weather'][0]['description']
    predicted_temperature_in_6_hrs = weather_forecast_data['list'][1]['main']['temp']

    # converting text to speech
    play_assistant_speech(
        f"In the next three hours the temperature will be {predicted_temperature_in_3_hrs} degrees Celsius"
        f", and it will be {predicted_weather_in_3_hrs}. After that, in 6 hours, the weather could be described as "
        f"{predicted_weather_in_6_hrs}, and it is predicted that the temperature will be about "
        f"{predicted_temperature_in_6_hrs} degrees Celsius")


def get_time():
    """
    This function tells user the exact time
    """
    # getting the time
    t = time.localtime()

    # converting text to speech
    play_assistant_speech(f"the current time is {t.tm_hour} hours {t.tm_min} minutes")

    # Easter egg - if hours are equals to minutes (e.g 11:11 or 22:22 etc) voice assistant asks the user to make a wish
    if t.tm_min == t.tm_hour:
        play_assistant_speech('quickly! make a wish')


def prepare_spotify_object():
    """
    This function prepares required information. I created an account as a spotify developer, obtained client secret and
    other required information. I saved this information in the file "spotify_developer_info".
    The function returns SpotifyObject which enables interaction with the spotify services

    source: https://www.geeksforgeeks.org/how-to-play-a-spotify-audio-with-python/
    """
    with open("spotify_developer_info", "r") as file:
        username, clientID, clientSecret, redirect_uri = [line.strip() for line in file]
        file.close()

    # authentication
    oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri)
    token_dict = oauth_object.get_access_token()
    token = token_dict['access_token']
    # creating spotify object
    spotifyObject = spotipy.Spotify(auth=token)
    return spotifyObject


def search_song_on_spotify(song_name, spotifyObject):
    """
    This function searches on spotify by the song title or the lyrics and opens in the browser the first song
    that appears in the results

    source: https://www.geeksforgeeks.org/how-to-play-a-spotify-audio-with-python/
    """
    # searching for a song
    results = spotifyObject.search(song_name, 1, 0, "track")
    songs_dict = results['tracks']
    song_items = songs_dict['items']
    song = song_items[0]['external_urls']['spotify']

    # opening song in the webbrowser (advantage - no need for authentication if the user is already signed in)
    webbrowser.open(song)

    # converting speech to text
    play_assistant_speech('Song has opened in your browser.')


def find_on_wikipedia(term):
    """
    This function performs search on wikipedia and returns either a short one sentence summary or asks the user
    to specify the prompt
    """
    try:
        # search on wikipedia
        result = wikipedia.summary(term, sentences=1)

        # converting text to speech
        play_assistant_speech(result)
    except:
        # asking the user to specify the query
        play_assistant_speech("there is a lot of articles on wikipedia, can you please specify the query?")


def tell_jokes():
    """
    This function tells jokes to user
    """
    joke = get_joke()

    # converting speech to text
    play_assistant_speech(joke)


def get_spotify_input(raw_query):
    """
    This function takes raw input, removes unnecessary words like "spotify" and using regular expressions it extracts
    the main query. The function returns the query if no match was found.
    """
    # removing unnecessary words from input
    query = re.sub(("(on|with|at|using|via) spotify"), '', raw_query)
    print(query)
    # Patterns for common search queries
    patterns = [
        r'(search|look|check|open|put) (in|on|at|up) \w+ for"" (.+)',  # e.g., "search on spotify for Gorillaz song"
        r'(.*)(play|turn on|open|turn|hear|put on|listen to) (.+)',            # e.g., Could you please turn on coldplay"
        r'(search|look for|find) (.+)',  # e.g., "can you search for I can buy myself flowers"
        r'((.*)song (.+))',  # e.g., "please find song baby shark"
        r'((.*)some (.+))'  # e.g. "i want to listen to some jazz"
    ]
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            return match.group(3).strip()

    # If no pattern matches, return the original query as the fallback
    return query


def extract_search_term(query):
    """
    This function uses regular expressions to extract the term for the search in wikipedia and returns the
    term if the match is found. If there is no match it returns original query
    """
    # Patterns for common search queries
    patterns = [
        r'(search|look|check) (in|on|at) \w+ for|"" (.+)', # e.g., "search on wikipedia for Beetle Juice"
        r'((who|what|where) is (.+))',            # e.g., "who is Putin?" "what is iron" "where is New York"
        r'(?:search|look for|find) (.+)',  # e.g., "search for AI"
        r'((give|explain) me (.+) about (.+))', # e.g., "give me info about Tesla"
        r'((.+) about (.+))'
    ]
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            return match.group(3).strip()

    # If no pattern matches, return the original query as the fallback
    return query


def get_intent(label, raw_text):
    """
    This function takes the label predicted by BERT and a raw input phrase. It then maps the label with an action
    function for the voice assistant
    """
    if label == "greeting":
        play_greetings()

    elif label == "farewell":
        play_farewells_and_quit()

    elif label == "current weather":
        get_current_weather(api_key, lat, lon)

    elif label == "weather forecast":
        get_weather_forecast(api_key, lat, lon)

    elif label == "time":
        get_time()

    elif label == "turn on music":
        # extracting name of the song
        spotify_input = get_spotify_input(raw_text)
        # searching for the song
        search_song_on_spotify(spotify_input, spotifyObject=prepare_spotify_object())

    elif label == "look in wikipedia":
        # extracting search term for wikipedia
        term = extract_search_term(raw_text)
        # searching for the term
        find_on_wikipedia(term)

    elif label == "joke":
        tell_jokes()

    else:
        play_failure_phrases()


if __name__ == "__main__":
    # setting up the assistant voice
    ttsEngine = pyttsx3.init()
    assistant = VoiceAssistant()
    assistant.name = "Marcus"
    assistant.sex = "male"

    setup_assistant_voice()

    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    api_key, lat, lon = weather_preparation()

    BERT_classifier = pipeline("text-classification", model="Amityukova/BERT_trained_for_voice_assistant")
    setup_assistant_voice()

    while True:
        voice_input = record_and_recognize_audio()

        if os.path.exists("microphone-results.wav"):
            os.remove("microphone-results.wav")

        print(colored(voice_input, "blue"))

        if voice_input:
            get_intent(get_label(BERT_classifier, voice_input),voice_input)

