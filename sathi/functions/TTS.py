from gtts import gTTS
import pygame
import os
from PyPDF2 import PdfReader, errors
from pathlib import Path

pygame.init()

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except errors.PdfReadError:
        print(f"Error reading PDF: {pdf_path}")
        return ""

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT: {txt_path} ({e})")
        return ""

def save_text_to_mp3(text, filename="output.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

def speak(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove(filename)

from pathlib import Path

def extract_filenames(folder_path="media/notes", extensions=[".pdf", ".txt"]):
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    
    file_list = [f.name for f in folder.iterdir() if f.is_file() and f.suffix in extensions]
    return len(file_list),file_list

def makemp3():
    folder_path = "media/notes"
    output_folder = "mp3"
    file_count, file_names = extract_filenames(folder_path)

    os.makedirs(output_folder, exist_ok=True)

    for file_name in file_names:
        file_path = Path(folder_path) / file_name
        mp3_filename = os.path.join(output_folder, f"{file_name}.mp3")

        if os.path.exists(mp3_filename):
            print(f"MP3 already exists: {mp3_filename}")
            continue

        print(f"Processing: {file_path}")

        if file_path.suffix == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif file_path.suffix == ".txt":
            text = extract_text_from_txt(file_path)
        else:
            print(f"Skipping unknown file type: {file_path}")
            continue

        if text.strip():
            save_text_to_mp3(text=text, filename=mp3_filename)
            print(f"Saved: {mp3_filename}")
        else:
            print(f"No text found in {file_path}")

makemp3()