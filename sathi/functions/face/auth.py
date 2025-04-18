# # Import OpenCV for video capture and image processing
# import cv2
# # Import face_recognition for face detection and encoding
# import face_recognition
# # Import numpy for numerical operations and array handling
# import numpy as np
# # Import os for file and directory operations
# import os
# # Import csv for reading and writing CSV files
# import csv
# # Import typing utilities for type hints
# from typing import List, Tuple, Set, Optional
# # Import PIL's Image class for image processing
# from PIL import Image
# # Import time for tracking elapsed time
# import time

# # Define constants
# IMAGE_FOLDER = "/home/subash/vs/padhai_sathi/sathi/functions/face/testimage"  # Change this to the path where your images are stored
# PROCESSED_FOLDER = "/home/subash/vs/padhai_sathi/sathi/functions/face/processedFolder"  # Folder where processed images will be moved
# CSV_FILENAME = "/home/subash/vs/padhai_sathi/sathi/functions/face/encoding.csv"  # Path to save the CSV file with face encodings

# # Number of frames to process in a batch for efficiency
# BATCH_SIZE = 3
# # Top-left coordinates of the static box for authentication zone
# STATIC_BOX_START = (150, 100)
# # Bottom-right coordinates of the static box for authentication zone
# STATIC_BOX_END = (450, 400)
# # Minimum confidence threshold for face authentication (70%)
# CONFIDENCE_THRESHOLD = 0.5  # Face recognition confidence threshold (70%)

# def append_face_encodings(image_path: str, student_name: str) -> None:
#     """
#     Append face encodings from an image to a CSV file with the student name and move the image to processed folder.
    
#     Args:
#         image_path: Path to the uploaded image.
#         student_name: Name of the student associated with the image.
#     """
#     # Check if the processed folder exists; create it if not
#     if not os.path.exists(PROCESSED_FOLDER):
#         # Create the processed folder
#         os.makedirs(PROCESSED_FOLDER)
    
#     # Load the image file using face_recognition
#     image = face_recognition.load_image_file(image_path)
#     # Generate face encodings from the image
#     face_encodings = face_recognition.face_encodings(image)
    
#     # Check if any face encodings were found
#     if face_encodings:
#         # Use the first face encoding (assuming one face per image)
#         face_encoding = face_encodings[0]
#         # Open the CSV file in append mode with no extra newlines
#         with open(CSV_FILENAME, mode="a", newline="") as file:
#             # Create a CSV writer object
#             writer = csv.writer(file)
#             # Write header if the file is empty
#             if os.stat(CSV_FILENAME).st_size == 0:
#                 # Write header with "Name" and 128 encoding fields
#                 writer.writerow(["Name"] + [f"Encoding_{i+1}" for i in range(128)])
#             # Write the student name and face encoding to the CSV
#             writer.writerow([student_name] + face_encoding.tolist())
#         # Print confirmation of encoding addition
#         print(f"Face encoding for {student_name} added to CSV")
        
#         # Get the base filename from the image path
#         filename = os.path.basename(image_path)
#         # Define the new path for the image in the processed folder
#         new_image_path = os.path.join(PROCESSED_FOLDER, filename)
#         # Move the image to the processed folder
#         os.rename(image_path, new_image_path)
#         # Print confirmation of image movement
#         print(f"Moved {filename} to {PROCESSED_FOLDER}")
#     else:
#         # Print warning if no faces were detected in the image
#         print(f"No face detected in {image_path}")

# def load_face_encodings() -> Tuple[List[np.ndarray], List[str]]:
#     """
#     Load face encodings and student names from a CSV file.
    
#     Returns:
#         Tuple of known face encodings and corresponding student names.
#     """
#     # Initialize empty lists for encodings and names
#     known_face_encodings = []
#     known_face_names = []
#     # Check if the CSV file exists
#     if os.path.exists(CSV_FILENAME):
#         # Open the CSV file in read mode
#         with open(CSV_FILENAME, mode="r") as file:
#             # Create a CSV reader object
#             reader = csv.reader(file)
#             # Skip the header row
#             next(reader, None)
#             # Iterate through each row in the CSV
#             for row in reader:
#                 # Extract the student name from the first column
#                 name = row[0]
#                 # Convert the encoding values (columns 1+) to a numpy array
#                 encoding = np.array(list(map(float, row[1:])), dtype=np.float32)
#                 # Append the name to the names list
#                 known_face_names.append(name)
#                 # Append the encoding to the encodings list
#                 known_face_encodings.append(encoding)
#     # Return the encodings and names as a tuple
#     return known_face_encodings, known_face_names

# def is_face_authenticated(face_encoding: np.ndarray, known_face_encodings: List[np.ndarray], known_face_names: List[str]) -> Optional[str]:
#     """
#     Check if a face encoding matches any known encoding with at least 70% confidence.
    
#     Args:
#         face_encoding: The face encoding to check.
#         known_face_encodings: List of known face encodings.
#         known_face_names: List of corresponding student names.
    
#     Returns:
#         str or None: Name of the matching student if confidence >= 0.7, None otherwise.
#     """
#     # Compare the face encoding with all known encodings
#     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#     # Calculate the face distances (lower is better)
#     face_distances = np.array(face_recognition.face_distance(known_face_encodings, face_encoding))
    
#     # Check if there are any matches and distances
#     if matches and len(face_distances) > 0:
#         # Find the index of the smallest distance
#         best_match_index = np.argmin(face_distances)
#         # Convert distance to confidence (1 - distance)
#         confidence = 1 - face_distances[best_match_index]
#         # Check if the best match is valid and meets the confidence threshold
#         if matches[best_match_index] and confidence >= CONFIDENCE_THRESHOLD:
#             # Return the corresponding student name
#             return known_face_names[best_match_index]
#     # Return None if no match is found
#     return None

# def draw_bounding_box(frame: np.ndarray, face_location: Tuple[int, int, int, int], student_name: Optional[str]) -> None:
#     """
#     Draw a bounding box with authentication status on the frame.
    
#     Args:
#         frame: Video frame to draw on.
#         face_location: Tuple of (top, right, bottom, left).
#         student_name: Name of the authenticated student, or None if not authenticated.
#     """
#     # Unpack the face location coordinates
#     top, right, bottom, left = face_location
#     # Determine if the face is authenticated
#     authenticated = student_name is not None
#     # Set color: green for authenticated, red for not authenticated
#     color = (0, 255, 0) if authenticated else (0, 0, 255)
#     # Draw a rectangle around the face
#     cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#     # Draw a filled rectangle for the text background
#     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
#     # Define the font for text
#     font = cv2.FONT_HERSHEY_DUPLEX
#     # Set the text based on authentication status
#     text = f"Authenticated: {student_name}" if authenticated else "Not Authenticated"
#     # Draw the text on the frame
#     cv2.putText(frame, text, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

# def process_batch(
#     frames: List[np.ndarray],
#     authenticated_faces: Set[int],
#     known_face_encodings: List[np.ndarray],
#     known_face_names: List[str]
# ) -> None:
#     """
#     Process a batch of frames for face recognition and authentication.
    
#     Args:
#         frames: List of video frames.
#         authenticated_faces: Set of face indices already authenticated in this session.
#         known_face_encodings: List of known face encodings.
#         known_face_names: List of corresponding student names.
#     """
#     # Iterate through each frame in the batch
#     for frame in frames:
#         # Resize the frame to 1/4 size for faster processing
#         small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         # Convert the frame to RGB (face_recognition uses RGB)
#         rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
#         # Detect face locations in the resized frame
#         face_locations = face_recognition.face_locations(rgb_small_frame)
#         # Generate face encodings for detected faces
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
#         # Iterate through each face encoding and location
#         for face_encoding, face_location in zip(face_encodings, face_locations):
#             # Scale face location back to original frame size
#             face_location = [v * 4 for v in face_location]
#             # Authenticate the face and get the student name
#             student_name = is_face_authenticated(face_encoding, known_face_encodings, known_face_names)
            
#             # Check if the face is within the static box
#             if (STATIC_BOX_START[0] < face_location[3] < STATIC_BOX_END[0] and
#                 STATIC_BOX_START[1] < face_location[0] < STATIC_BOX_END[1]):
#                 # Generate a unique ID for the face encoding
#                 face_id = hash(str(face_encoding))
#                 # Check if the face is authenticated and not previously processed
#                 if student_name and face_id not in authenticated_faces:
#                     # Calculate confidence for logging
#                     confidence = 1 - face_recognition.face_distance(known_face_encodings, face_encoding).min()
#                     # Print authentication confirmation
#                     print(f"Authenticated: {student_name} (Confidence: {confidence:.2f})")
#                     # Add face ID to authenticated set
#                     authenticated_faces.add(face_id)
#                 # Print message if not authenticated
#                 elif not student_name:
#                     print("Not Authenticated")
            
#             # Draw bounding box on the frame
#             draw_bounding_box(frame, face_location, student_name)

# def main():
#     """
#     Main loop for video capture and face recognition.
#     """
#     # Initialize a set to track authenticated faces
#     authenticated_faces = set()
#     # Record the start time for reset intervals
#     last_reset_time = time.time()
#     # Initialize video capture from default webcam (index 0)
#     video_capture = cv2.VideoCapture(0)
#     # Initialize a list to store frames for batch processing
#     frame_batch = []
    
#     # Load known face encodings and names from CSV
#     known_face_encodings, known_face_names = load_face_encodings()
    
#     try:
#         # Run the main loop indefinitely
#         while True:
#             # Read a frame from the video capture
#             ret, frame = video_capture.read()
#             # Check if the frame was read successfully
#             if not ret:
#                 # Break the loop if no frame is captured
#                 break
            
#             # Add the frame to the batch
#             frame_batch.append(frame)
#             # Draw the static box on the frame
#             cv2.rectangle(frame, STATIC_BOX_START, STATIC_BOX_END, (0, 255, 0), 2)
            
#             # Process the batch when it reaches the specified size
#             if len(frame_batch) == BATCH_SIZE:
#                 # Process the batch of frames
#                 process_batch(
#                     frame_batch, authenticated_faces, known_face_encodings, known_face_names
#                 )
#                 # Clear the batch for the next set of frames
#                 frame_batch = []
            
#             # Display the frame in a window named 'Video'
#             cv2.imshow('Video', frame)
            
#             # Check for 'q' key press to exit
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 # Break the loop if 'q' is pressed
#                 break
    
#     finally:
#         # Release the video capture device
#         video_capture.release()
#         # Close all OpenCV windows
#         cv2.destroyAllWindows()

# def test_authentication(test_image_path: str) -> None:
#     """
#     Test face authentication using a single image against stored encodings.
    
#     Args:
#         test_image_path: Path to the test image.
#     """
#     # Load known encodings and names
#     known_face_encodings, known_face_names = load_face_encodings()
    
#     # Load and process the test image
#     if not os.path.exists(test_image_path):
#         print(f"Test image {test_image_path} does not exist")
#         return
    
#     image = face_recognition.load_image_file(test_image_path)
#     face_encodings = face_recognition.face_encodings(image)
    
#     if face_encodings:
#         # Use the first face encoding
#         face_encoding = face_encodings[0]
#         # Authenticate the face
#         student_name = is_face_authenticated(face_encoding, known_face_encodings, known_face_names)
#         if student_name:
#             confidence = 1 - face_recognition.face_distance(known_face_encodings, face_encoding).min()
#             print(f"Test image authenticated as {student_name} (Confidence: {confidence:.2f})")
#             print(student_name)
#         else:
#             print("Test image not authenticated")
#     else:
#         print(f"No face detected in test image {test_image_path}")
#     return student_name

# if __name__ == "__main__":
#     # Ensure the image folder exists
#     if not os.path.exists(IMAGE_FOLDER):
#         # Create the image folder
#         os.makedirs(IMAGE_FOLDER)
#     # Ensure the processed folder exists
#     if not os.path.exists(PROCESSED_FOLDER):
#         # Create the processed folder
#         os.makedirs(PROCESSED_FOLDER)
    
#     # Process all images in the image folder
#     for filename in os.listdir(IMAGE_FOLDER):
#         # Check if the file is an image
#         if filename.lower().endswith((".jpeg", ".jpg", ".png")):
#             # Derive student name from filename (without extension)
#             student_name = os.path.splitext(filename)[0]
#             # Construct the full image path
#             image_path = os.path.join(IMAGE_FOLDER, filename)
#             # Process the image to append encodings
#             append_face_encodings(image_path, student_name)
    

#     # Start the main authentication loop
# test_authentication(test_image_path="/home/subash/vs/padhai_sathi/sathi/functions/face/testimage/arik.jpg")