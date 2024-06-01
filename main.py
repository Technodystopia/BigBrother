import cv2
import numpy as np
import telepot
import pyttsx3
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
from datetime import datetime
import face_recognition
import pygame

# Setup GPIO
DOORBELL_PIN = 18  # GPIO pin for the doorbell button
LED_PIN = 23       # GPIO pin for the LED light panel
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOORBELL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

# Setup Camera
camera = PiCamera()

# Setup Telegram Bot
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
TELEGRAM_CHAT_ID = 'your_telegram_chat_id'
bot = telepot.Bot(TELEGRAM_BOT_TOKEN)

# Setup Text-to-Speech
engine = pyttsx3.init()

# Initialize Pygame for Display and Sound
pygame.init()
screen = pygame.display.set_mode((800, 480))  # Adjust resolution to your screen size
pygame.display.set_caption('Doorbell Camera')
pygame.mixer.init()
doorbell_sound = pygame.mixer.Sound('doorbell.wav')  # Load the doorbell sound

# Load Reference Images and Create Face Encodings
def load_reference_images():
    known_face_encodings = []
    known_face_names = []
    
    # Load your reference images and generate encodings here
    # Example:
    # image = cv2.imread('reference_image.jpg')
    # rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # encodings = face_recognition.face_encodings(rgb_image)[0]
    # known_face_encodings.append(encodings)
    # known_face_names.append("Person Name")
    
    return known_face_encodings, known_face_names

known_face_encodings, known_face_names = load_reference_images()

# Function to capture image and detect face
def capture_and_detect():
    # Play doorbell sound
    doorbell_sound.play()
    
    # Turn on the LED light
    GPIO.output(LED_PIN, GPIO.HIGH)
    
    # Capture image
    image_path = '/home/pi/image.jpg'
    camera.capture(image_path)
    
    # Turn off the LED light
    GPIO.output(LED_PIN, GPIO.LOW)
    
    # Load the captured image
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect faces in the image
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        
        # Annotate image with the name
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(image, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        
        # Save the annotated image
        cv2.imwrite(image_path, image)
        
        # Send image to Telegram
        bot.sendPhoto(TELEGRAM_CHAT_ID, photo=open(image_path, 'rb'), caption=name)
        
        # Announce name through speaker
        engine.say(f"Detected {name}")
        engine.runAndWait()
        
    # Display image on screen
    img = pygame.image.load(image_path)
    screen.blit(img, (0, 0))
    pygame.display.update()

# Main Loop
try:
    print("Waiting for doorbell press...")
    while True:
        button_state = GPIO.input(DOORBELL_PIN)
        if button_state == GPIO.LOW:
            print("Doorbell pressed!")
            capture_and_detect()
            sleep(5)  # Debounce delay
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
    pygame.quit()
