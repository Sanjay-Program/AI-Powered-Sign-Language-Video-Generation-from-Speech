import os
import speech_recognition as sr
from gtts import gTTS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips

# Initialize the recognizer
recognizer = sr.Recognizer()

# Record audio from the user
with sr.Microphone() as source:
    print("Say something...")
    audio = recognizer.listen(source)
    print("Recording complete.")

# Convert audio to English text
try:
    # Recognize English text
    text = recognizer.recognize_google(audio, language='en-IN')
    print(f"Text: {text}")

    # Language in which you want to convert
    language = 'en'

    # Creating the gTTS object for audio conversion
    tts = gTTS(text=text, lang=language, slow=False)
    audio_file = "output.mp3"
    tts.save(audio_file)

    # Process the text using NLP to extract main words
    nltk.download('punkt')
    nltk.download('stopwords')

    # Tokenize the text
    words = word_tokenize(text)

    # Get the default stopwords and remove 'stop' from the list
    stop_words = set(stopwords.words('english'))
    stop_words.discard('stop')

    # Filter out punctuation, stopwords, and lowercase the text
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words and word not in string.punctuation]

    print(f"Main words: {filtered_words}")

except sr.UnknownValueError:
    print("Sorry, I could not understand the audio.")
except sr.RequestError as e:
    print(f"Sorry, there was an error with the request: {e}")

# Directory where images are stored
image_dir = 'sign_language/signs'  # Replace with your actual image directory path

# List to store full image file paths
image_list = []

# Loop through the filtered words to find corresponding images
for word in filtered_words:
    image_file = os.path.join(image_dir, f"{word}.png")  # Assuming images are named as "word.png"
    if os.path.isfile(image_file):
        image_list.append(image_file)
    else:
        print(f"Image for word '{word}' not found.")

# Check if any images were found
if not image_list:
    print("No matching images found for the filtered words.")
else:
    # Set the duration for each image in the video
    frame_duration = 1  # Duration in seconds for each image

    # Load the images directly using moviepy
    clips = [ImageSequenceClip([img], durations=[frame_duration]) for img in image_list]

    # Concatenate the image clips into one video
    video_clip = concatenate_videoclips(clips, method="compose")

    # Combine the audio with the video
    try:
        audio_clip = AudioFileClip(audio_file)

        # Set the audio to the video
        final_video = video_clip.set_audio(audio_clip)
        final_video.write_videofile("final_output.mp4", codec="libx264", fps=24)

        print("Video with audio created successfully.")
    except Exception as e:
        print(f"Error in combining video and audio: {e}")
