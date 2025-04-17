import os
import speech_recognition as sr
from gtts import gTTS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip

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

# Check if any images were found
if not image_list:
    print("No matching images found for the filtered words.")
else:
    # Initialize video writer using the first image to set video size
    frame = cv2.imread(image_list[0])
    height, width, _ = frame.shape
    video = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1, (width, height))

    # Loop through each image in the list and write it to the video
    for image_name in image_list:
        image = cv2.imread(image_name)
        video.write(image)

    # Release the video writer
    video.release()
    cv2.destroyAllWindows()

    print("Video generated successfully.")

    # Combine the audio with the video
    try:
        video_clip = VideoFileClip('output_video.mp4')
        audio_clip = AudioFileClip('output.mp3')

        # Set the audio to the video
        final_video = video_clip.set_audio(audio_clip)
        final_video.write_videofile("final_output.mp4", codec="libx264")

        print("Video with audio created successfully.")
    except Exception as e:
        print(f"Error in combining video and audio: {e}")
