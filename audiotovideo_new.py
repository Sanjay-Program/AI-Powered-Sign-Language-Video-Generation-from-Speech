import os
import speech_recognition as sr
from gtts import gTTS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string
from nltk import pos_tag
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Download necessary NLTK data if not already downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Initialize the recognizer
recognizer = sr.Recognizer()

def record_audio():
    """Record audio from the microphone and return the recognized text."""
    with sr.Microphone() as source:
        logging.info("Say something...")
        audio = recognizer.listen(source)
        logging.info("Recording complete.")
    try:
        # Recognize English text
        text = recognizer.recognize_google(audio, language='en-IN')
        logging.info(f"Text: {text}")
        return text
    except sr.UnknownValueError:
        logging.error("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        logging.error(f"Error with the request: {e}")
        return None

def convert_text_to_audio(text):
    """Convert text to audio and save it as an MP3 file."""
    language = 'en'
    tts = gTTS(text=text, lang=language, slow=False)
    audio_file = "output.mp3"
    tts.save(audio_file)
    return audio_file

def process_text(text):
    """Process the text to extract main words, sentences, and verbs."""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    stop_words.discard('stop')  # Remove 'stop' from stopwords
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words and word not in string.punctuation]
    
    # POS tagging
    pos_tags = pos_tag(words)
    verbs = [word for word, pos in pos_tags if pos.startswith('VB')]  # Extract verbs

    logging.info(f"Main words: {filtered_words}")
    logging.info(f"Extracted verbs: {verbs}")
    return filtered_words, sentences, verbs

def find_images(filtered_words, image_dir):
    """Find images corresponding to the filtered words."""
    image_list = []
    for word in filtered_words:
        image_file = os.path.join(image_dir, f"{word}.png")  # Assuming images are named as "word.png"
        if not os.path.isfile(image_file):
            # Try different formats if PNG is not found
            for ext in ['.jpg', '.jpeg', '.png']:
                image_file = os.path.join(image_dir, f"{word}{ext}")
                if os.path.isfile(image_file):
                    break
        if os.path.isfile(image_file):
            image_list.append(image_file)
        else:
            logging.warning(f"Image for word '{word}' not found.")
    return image_list

def calculate_durations(filtered_words):
    """Calculate durations for each word based on syllable count or fixed duration."""
    return [len(word) * 0.5 for word in filtered_words]  # Example: 0.5 seconds per syllable

def create_video_from_images_and_audio(image_list, audio_file, durations):
    """Create a video from the list of images and the audio file."""
    if not image_list:
        logging.error("No matching images found for the filtered words.")
        return

    # Load images with the respective durations
    clips = [ImageSequenceClip([img], durations=[duration]) for img, duration in zip(image_list, durations)]

    # Concatenate the image clips into one video
    video_clip = concatenate_videoclips(clips, method="compose")

    try:
        audio_clip = AudioFileClip(audio_file)
        final_video = video_clip.set_audio(audio_clip)
        final_video.write_videofile("final_output.mp4", codec="libx264", fps=24)
        logging.info("Video with audio created successfully.")
    except Exception as e:
        logging.error(f"Error in combining video and audio: {e}")

def main():
    text = record_audio()
    if text:
        audio_file = convert_text_to_audio(text)
        filtered_words, sentences, verbs = process_text(text)

        # Output the verbs and sentences
        logging.info(f"Extracted Sentences: {sentences}")
        logging.info(f"Extracted Verbs: {verbs}")

        image_dir = 'sign_language/signs'  # Update with your actual image directory
        image_list = find_images(filtered_words, image_dir)

        # Calculate durations for the images
        durations = calculate_durations(filtered_words)

        create_video_from_images_and_audio(image_list, audio_file, durations)

if __name__ == "__main__":
    main()
