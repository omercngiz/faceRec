import os
import cv2
import json

def load_face_database(face_app, db_path='face_db'):
    """
    Loads face database from storage directory
    Returns list of person dictionaries with metadata and embeddings
    """
    face_db = []  # Will store all face database entries
    
    # Create database directory if it doesn't exist
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    # Process each person directory in the database
    for person_name in os.listdir(db_path):
        person_dir = os.path.join(db_path, person_name)
        
        # Skip non-directory items
        if not os.path.isdir(person_dir):
            continue

        # Read person metadata from info.json
        info_path = os.path.join(person_dir, "info.json")
        if not os.path.exists(info_path):
            continue  # Skip directories without metadata

        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                # Extract person details with defaults
                name = info.get("name", person_name)
                age = info.get("age", 0)
                gender = info.get("gender", "Unknown")
        except json.JSONDecodeError:
            continue  # Skip invalid JSON files

        # Process all images in person directory
        embeddings = []
        for img_file in os.listdir(person_dir):
            # Skip non-image files
            if not img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            img_path = os.path.join(person_dir, img_file)
            img = cv2.imread(img_path)
            
            # Skip unreadable images
            if img is None:
                continue

            # Extract face embeddings from image
            faces = face_app.get(img)
            if faces:
                # Use first detected face
                embeddings.append(faces[0].embedding)

        # Add person to database if embeddings found
        if embeddings:
            face_db.append({
                "name": name,
                "age": age,
                "gender": gender,
                "embeddings": embeddings
            })

    return face_db

def save_new_person(name, surname, age, gender, images):
    """
    Saves new person to face database
    Creates directory structure and stores images with metadata
    """
    # Create person directory
    person_name = f"{name}_{surname}"
    base_dir = os.path.join("face_db", person_name)
    os.makedirs(base_dir, exist_ok=True)

    # Create and save metadata
    info = {
        "name": person_name,
        "age": age,
        "gender": gender
    }
    with open(os.path.join(base_dir, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    # Save all captured images
    for idx, img in enumerate(images, 1):
        cv2.imwrite(os.path.join(base_dir, f"{idx}.png"), img)