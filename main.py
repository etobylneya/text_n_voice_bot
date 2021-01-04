import telebot
import speech_recognition as sr
import os
from gtts import gTTS
import subprocess



bot = telebot.TeleBot('PASTE_YOUR_BOT_TOKEN_HERE')

# a function to determine the language of a text message
# the bot only supports 2 languages - Eng and Rus.
def lang(message):
    cyr = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
    # 2 counters to count  cyrillic letters for Russian and latin for English
    ru_cntr = 0
    en_cntr = 0

    for letter in str(message.text):
        letter = letter.lower()
        if letter in cyr:
            ru_cntr += 1
        elif letter.isascii() and letter.isalnum() and not letter.isnumeric():
            en_cntr += 1
    # checking whether there were more cyrillic letters or latin letters
    if ru_cntr > en_cntr:
        language = 'ru'
    else:
        language = 'en'
    return language

# handling text messages
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    language = lang(message)
    # generating speech out of the text
    speech = gTTS(text=message.text, lang=language, slow=False)
    speech.save("speech_bot.ogg")
    # sending the speech saved in .ogg format
    with open("speech_bot.ogg", 'rb') as audio:
        bot.send_voice(message.from_user.id, audio)
    # deleting the speech file for privacy reasons
    os.remove("speech_bot.ogg")

#handling voice and audio messages
# transcribing voice and audio messages
@bot.message_handler(content_types=['voice', 'audio'])
def get_audio_messages(message):

    r = sr.Recognizer()
    # downloading  the voice message
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    # saving the voice message
    with open('user_voice.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    # converting the audio to .wav format; .ogg is not supported by speech_recognition
    src_filename = 'user_voice.ogg'
    dest_filename = 'user_voice_output.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    if process.returncode != 0:
        raise Exception("Something went wrong with audio conversion")
    # converting audio to an audio file
    user_audio_file = sr.AudioFile("user_voice_output.wav")
    # converting audio file to audio data
    with user_audio_file as source:
        user_audio = r.record(source)
    # removing the saved files for privacy reasons
    os.remove('user_voice.ogg')
    os.remove('user_voice_output.wav')
    # declaring variables for speech recognition in Rus and Eng
    text_ru = ''
    text_en = ''
    # try recognizing the speech both in Russian and English; save the transcription to a corresponding variable
    try:
        text_ru = r.recognize_google(user_audio, language='ru')
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        pass
    try:
        text_en = r.recognize_google(user_audio, language='en-US')
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        pass
    # compare the length of the transcription. Send whichever is longer
    if len(text_ru) > len(text_en):
        bot.send_message(message.from_user.id, text_ru)
    elif len(text_en) > len(text_ru):
        bot.send_message(message.from_user.id, text_en)
    else:
        bot.send_message(message.from_user.id, 'I\'m sorry, but I couldn\'t transcribe your audio.')


bot.polling(none_stop=True, interval=0)
