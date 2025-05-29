import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

class Recognizer:
    def __init__(self):
        """Initialize face recognition system with InsightFace model"""
        # Configure face analysis model to use CPU
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        # Prepare model with default context and detection size
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))
        
        # Set similarity threshold for recognizing known faces
        self.similarity_threshold = 0.4

    def recognize_faces(self, frame, face_db):
        """Process frame to detect and recognize faces"""
        # Flag to track if any unknown faces are detected
        unknown_detected = False

        # Detect all faces in the current frame
        faces = self.face_app.get(frame)

        # Process each detected face
        for face in faces:
            # Get face embedding vector
            embedding = face.embedding

            # Find best match in database
            name, age, gender, similarity = self.find_match(embedding, face_db)

            # Get bounding box coordinates
            x1, y1, x2, y2 = [int(coord) for coord in face.bbox]
            
            # Set color based on recognition status
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw bounding box around face
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label text
            label = name
            if name != "Unknown":
                label += f" | {gender}, {age}"
            else:
                unknown_detected = True
                
            # Display label below bounding box
            cv2.putText(frame, label, (x1, y2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame, unknown_detected

    def find_match(self, embedding, face_db):
        """Find best matching face in database using cosine similarity"""
        best_score = 0  # Track highest similarity score
        best_match = None  # Track best matching person
        
        # Reshape embedding to 2D array for cosine similarity calculation
        embedding = np.array(embedding).reshape(1, -1)
        
        # Search through all persons in database
        for person in face_db:
            # Convert stored embeddings to numpy array
            db_embeddings = np.array(person["embeddings"])
            
            # Skip if no embeddings available
            if db_embeddings.size == 0:
                continue
                
            # Calculate similarity scores
            scores = cosine_similarity(embedding, db_embeddings)
            max_score = np.max(scores)  # Get highest score for this person
            
            # Update best match if current score is higher
            if max_score > best_score:
                best_score = max_score
                best_match = person

        # Return match if above threshold, otherwise unknown
        if best_score >= self.similarity_threshold and best_match:
            return (
                best_match["name"],
                best_match["age"],
                best_match["gender"],
                best_score
            )
        else:
            return "Unknown", None, None, best_score