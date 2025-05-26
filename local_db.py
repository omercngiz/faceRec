import os
import cv2
import json

def load_face_database(face_app, db_path='face_db'):
    face_db = []

    if not os.path.exists(db_path):
        os.makedirs(db_path)

    for person_name in os.listdir(db_path):
        person_dir = os.path.join(db_path, person_name)
        if not os.path.isdir(person_dir):
            continue

        # info.json'u oku
        info_path = os.path.join(person_dir, "info.json")
        if not os.path.exists(info_path):
            print(f"[WARN] info.json bulunamadı: {person_dir}")
            continue

        with open(info_path, 'r', encoding='utf-8') as f:
            try:
                info = json.load(f)
                name = info.get("name", person_name)
                age = info.get("age", 0)
                gender = info.get("gender", "Bilinmiyor")
            except:
                print(f"[HATA] info.json okunamadı: {info_path}")
                continue

        embeddings = []
        for img_file in os.listdir(person_dir):
            if not img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            img_path = os.path.join(person_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                continue

            faces = face_app.get(img)
            if len(faces) == 0:
                print(f"[INFO] Yüz bulunamadı: {img_path}")
                continue

            embeddings.append(faces[0].embedding)

        if len(embeddings) > 0:
            face_db.append({
                "name": name,
                "age": age,
                "gender": gender,
                "embeddings": embeddings
            })
        else:
            print(f"[INFO] Yüz embedding bulunamadı: {person_dir}")

    return face_db

def save_new_person(name, surname, age, gender, images):
    person_name = f"{name}_{surname}"
    base_dir = os.path.join("face_db", person_name)
    os.makedirs(base_dir, exist_ok=True)

    # Meta bilgileri yaz
    info = {
        "name": person_name,
        "age": age,
        "gender": gender
    }
    with open(os.path.join(base_dir, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    # Görselleri sırayla kaydet
    for idx, img in enumerate(images, 1):
        cv2.imwrite(os.path.join(base_dir, f"{idx}.png"), img)
