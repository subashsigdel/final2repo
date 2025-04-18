# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import Note, User
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .functions.STT import transcribe_audio_file,convert_to_wav
from .functions.Voicecommand import listen_and_respond,listen_and_respond_pdf
from .functions.TTS import speak,extract_filenames
import speech_recognition as sr
from pydub import AudioSegment
import speech_recognition as sr
import os
from django.urls import reverse
from django.conf import settings
import os
import time
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages
from threading import Timer
# from .functions.face.auth import test_authentication
# import face_recognition
import pygame
from django.utils import timezone
def test(request):
    return render(request,"test.html")


@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        tomp3 = None
        try:
            tomp3 = convert_to_wav(audio_file)
            texts = transcribe_audio_file(tomp3)
            textlast = listen_and_respond(command=texts)
            print(textlast)

            if textlast == "MakeNotes":
                return JsonResponse({'redirect': '/make_notes/'})
            elif textlast == "ReturnHome":
                speak("Back to dashboard")
                return JsonResponse({'redirect': '/dashboard_student/'})
            elif textlast == "ListenNotes":
                speak("say notes name")
                return JsonResponse({'redirect': '/student_notes/'})
            elif textlast == "AskQuestion":
                speak("ask question")
                return JsonResponse({'redirect': '/student_ask/'})
            else:
                return JsonResponse({'error': 'No valid command recognized'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if tomp3 and os.path.exists(tomp3):
                time.sleep(5)  # Delay 5 seconds before deletion
                os.remove(tomp3)

    return JsonResponse({'error': 'No audio file received'}, status=400)

import os
import time
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Optional if CSRF token isn't handled on frontend
def save_note_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        tomp3 = None
        try:
            # Convert audio file to WAV format if necessary
            tomp3 = convert_to_wav(audio_file)

            # Transcribe audio to text
            texts = transcribe_audio_file(tomp3).strip()

            # Get first two words for filename
            first_two_words = "_".join(texts.split()[:2]).lower()
            if not first_two_words:
                first_two_words = f"note_{int(time.time())}"

            # Clean filename (remove special characters)
            first_two_words = "".join(c for c in first_two_words if c.isalnum() or c == '_')

            unique_filename = f"{first_two_words}.txt"

            # Define the path for the text file
            text_file_path = os.path.join('media/notes', unique_filename)

            # Save the transcribed text to the file
            with open(text_file_path, 'w') as text_file:
                text_file.write(texts)

            return JsonResponse({'success': True, 'message': 'Audio processed and text saved successfully.', 'filename': unique_filename})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        finally:
            if tomp3 and os.path.exists(tomp3):
                time.sleep(5)  # Delay 5 seconds before deletion
                os.remove(tomp3)

    return JsonResponse({'error': 'No audio file received'}, status=400)


# views.py
import base64
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def save_image(request):
#     if request.method == 'POST':
#         try:
#             # Get the image data from the request
#             data = request.body.decode('utf-8')
#             image_data = base64.b64decode(data.split(',')[1])  # Get the image part of the base64 string
            
#             # Define the folder where images will be saved
#             folder = os.path.join(settings.MEDIA_ROOT, 'captured_images')
#             os.makedirs(folder, exist_ok=True)

#             # Create a unique filename
#             filename = f"student.jpg"
#             file_path = os.path.join(folder, filename)

#             # Write the image to a file
#             with open(file_path, 'wb') as file:
#                 file.write(image_data)

#             return JsonResponse({'message': 'Image saved successfully', 'filename': filename}, status=200)

#         except Exception as e:
#             return JsonResponse({'message': str(e)}, status=500)

#     return JsonResponse({'message': 'Invalid request'}, status=400)

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages

User = get_user_model()

def teacher_student(request):
    search_query = request.GET.get("search", "")
    students = User.objects.filter(user_type="student")

    if search_query:
        students = students.filter(first_name__icontains=search_query)

    return render(request, "student_detail.html", {
        "students": students
    })
def landing(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('login')

        user = User(name=name, email=email, user_type='teacher')

        user = User(name=name, email=email, user_type="teacher")

        user.set_password(password)
        user.save()
        login(request, user)
        return redirect('dashboard')  # Redirect to dashboard after registration

    return render(request, 'register.html')

@login_required
def register_student(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        # Check if the user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('teacher_student')

        # Create the user with user_type=student (you may be using a custom user model)
        user = User.objects.create(
            name=name,
            email=email,
            password=make_password("student123"),  # Default password
            user_type="student"
        )
        messages.success(request, "Student registered successfully.")
        return redirect('teacher_student')



# import os
# import csv
# import face_recognition
# import numpy as np
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from django.conf import settings
# import base64
# import os
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings

import base64
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import base64
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import base64
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import base64
import os
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings




import os
import time
import base64
from django.http import JsonResponse
from django.conf import settings


def delete_all_images_in_folder(folder_path):
    """Delete all files in the folder."""
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting files: {str(e)}")

def save_image(request):
    if request.method == 'POST':
        try:
            # Get the image data from the request
            data = request.body.decode('utf-8')
            image_data = base64.b64decode(data.split(',')[1])  # Get the image part of the base64 string

            # Define the folder where images will be saved
            folder = os.path.join(settings.MEDIA_ROOT, 'captured_images')
            os.makedirs(folder, exist_ok=True)

            # Create a unique filename
            filename = f"student.jpg"
            file_path = os.path.join(folder, filename)

            # Write the image to a file
            with open(file_path, 'wb') as file:
                file.write(image_data)

            # Set a timer to delete everything in the folder after 13 seconds
            Timer(13, delete_all_images_in_folder, [folder]).start()

            return JsonResponse({'message': 'Image saved successfully', 'filename': filename}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)




from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User  # Import the custom User model

def login_student_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print("Login attempt:", email, password)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            print("User found:", user)
            if user.user_type == 'student':
                login(request, user)
                return redirect('dashboard_student')
            else:
                messages.error(request, "Access denied. Only students can log in here.")
        else:
            print("Authentication failed")
            messages.error(request, "Invalid email or password.")

    return render(request, 'login_student.html')



 # You can create a simple page with a process button



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # This works now
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')
# pip install face_recognition


import os
import time
from django.http import JsonResponse

import os
import time
from django.shortcuts import render
from django.http import JsonResponse

import os
from django.conf import settings
from django.http import JsonResponse
import os
import time
import difflib
import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

def notes_view_student(request):
    # Step 1: Get existing notes filenames
    file_count, filenames = extract_filenames(folder_path="media/notes")
    context = {'notes': filenames}
    print(f"[DEBUG] Existing notes: {context}")

    if request.method == 'POST':
        # Step 2: Handle AJAX delete request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                note_to_delete = data.get('note_name')

                if note_to_delete:
                    file_path = os.path.join(settings.MEDIA_ROOT, 'notes', note_to_delete)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        return JsonResponse({
                            'success': True,
                            'message': f'{note_to_delete} deleted successfully'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'File not found'
                        })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'No note name provided'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })

        # Step 3: Handle audio upload and processing
        elif request.FILES.get('audio_file'):
            audio_file = request.FILES['audio_file']
            tomp3 = None
            try:
                # Convert uploaded audio to WAV
                tomp3 = convert_to_wav(audio_file)
                print(f"[DEBUG] Converted audio file: {tomp3}")

                # Transcribe the audio
                texts = transcribe_audio_file(tomp3)
                print(f"[DEBUG] Transcribed text: {texts}")

                # Find matching command
                commands = listen_and_respond_pdf(texts)
                print(f"[DEBUG] Command extracted: {commands}")

                # Search for matching mp3 file
                folder_path = "mp3"
                all_files = os.listdir(folder_path)
                file_names_without_ext = [os.path.splitext(file)[0] for file in all_files]
                
                print(f"[DEBUG] Files available for matching: {file_names_without_ext}")

                # Using fuzzy matching
                match = difflib.get_close_matches(commands.lower(), file_names_without_ext, n=1, cutoff=0.6)

                if match:
                    matching_filename = match[0] + '.mp3'
                    matching_file = os.path.join(folder_path, matching_filename)
                    print(f"[DEBUG] Found matching file: {matching_file}")

                    # Play the matched file
                    speak(matching_file)

                    context['success'] = True
                    context['message'] = f'Found and played file: {matching_filename}'
                else:
                    print(f"[DEBUG] No matching file found for command: {commands}")
                    context['success'] = False
                    context['error'] = 'No matching file found for the command.'

            except Exception as e:
                print(f"[DEBUG] Exception occurred: {str(e)}")
                context['success'] = False
                context['error'] = str(e)

            finally:
                if tomp3 and os.path.exists(tomp3):
                    time.sleep(5)
                    os.remove(tomp3)
                    print(f"[DEBUG] Temporary file {tomp3} deleted.")

            return render(request, 'student_notes.html', context)

    # Step 4: Handle normal GET request
    context['success'] = False
    context['error'] = 'No audio file received.'
    return render(request, 'student_notes.html', context)




@csrf_exempt
def stop_music(request):
    if request.method == 'POST':
        try:
            pygame.mixer.music.stop()
            return JsonResponse({'success': True, 'message': 'Music stopped.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def dashboard_view_student(request):
    return render(request, 'student_dashboard.html')

def make_notes_view_student(request):
    return render(request, 'student_make_notes.html')





from .models import Question




from django.http import JsonResponse
from django.shortcuts import render, redirect
import os
import time
def ask_view_student(request):
    transcribed_text = None

    if request.method == 'POST':
        if request.FILES.get('audio_file'):
            audio_file = request.FILES['audio_file']
            tomp3 = None
            try:
                # Convert audio file to WAV format if necessary
                tomp3 = convert_to_wav(audio_file)

                # Transcribe audio to text
                transcribed_text = transcribe_audio_file(tomp3)
                print("done")

                # Prepare title (first 2 words of transcribed text)
                title_words = transcribed_text.split()[:2]
                title = ' '.join(title_words) if title_words else 'Untitled'

                # Save to database
                saved_question = Question.objects.create(
                    user=request.user,
                    name=title,
                    question=transcribed_text
                )
                print(f"Saved Question - Title: {saved_question.name}, Question: {saved_question.question}")

                return JsonResponse({
                    'success': True,
                    'message': 'Audio processed and saved successfully.',
                    'transcribed_text': transcribed_text
                })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

            finally:
                if tomp3 and os.path.exists(tomp3):
                    os.remove(tomp3)

        else:
            # Handle Save Note form submission
            title = request.POST.get('title')
            content = request.POST.get('content')

            if title and content:
                Question.objects.create(
                    user=request.user,
                    name=title,
                    question=content
                )
                return redirect('student_ask')  # redirect back to form page or dashboard

    return render(request, 'student_ask.html')






def get_all_questions(request):
    questions = Question.objects.filter(user=request.user)
    return render(request, 'teacher_questions.html', {'questions': questions})



def dashboard_view(request):
    # Query to get all students (make sure the user_type field exists in your model)
    students = User.objects.filter(user_type='student')

    num_students = User.objects.filter(user_type='student').count()

    # Get the count of notes
    num_notes = Note.objects.count()

    # Pass these values to the template
    return render(request, 'teacher_dashboard.html', {
        'num_students': num_students,
        'num_notes': num_notes,
        'students': students
    })

def teacher_student_add_view(request):
    students = User.objects.filter(user_type='student')
    return render(request, 'teacher_add.html', {'students': students})

def teacher_notes(request):
    return render(request, 'teacher_notes.html')

@login_required
def create_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        pdf_file = request.FILES.get('pdf')

        if not title or not subject:
            return HttpResponseBadRequest('Title and Subject are required.')

        note = Note(
            user=request.user,
            title=title,
            subject=subject,
            date=timezone.now()  # Manually set current datetime
        )

        if pdf_file:
            note.file = pdf_file

        # If content is needed, store it in another model field or logic
        note.save()
        return redirect('teacher_notes')

    return render(request, 'teacher_notes.html')

import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Note  # Adjust if the model is imported differently

@login_required
def note_list(request):
    file_count, filenmaes = extract_filenames(folder_path="media/notes")
    context = {'notes': filenmaes}
    print(context)
    # Render the template with notes and files
    return render(request, 'teacher_notes.html', {'notes': filenmaes})


@login_required
def teacher_notes(request):
    query = request.GET.get('search', '')
    if query:
        notes = Note.objects.filter(title__icontains=query)
    else:
        notes = Note.objects.all()
    return render(request, '.html', {'notes': notes, 'query': query})



def logout_view(request):
    logout(request)
    return redirect('Landing')