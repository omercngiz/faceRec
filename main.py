import local_db
import gui
import tkinter as tk

from tkinter import messagebox
from recognize import Recognizer

def main():
    # InsightFace ve tanıma sistemi başlatılıyor
    recognizer = Recognizer()
    face_db = local_db.load_face_database(recognizer.face_app)
    
    def recognize_wrapper(frame, db):
        return recognizer.recognize_faces(frame, db)

    def add_person_handler():
        main_gui.pause_camera()
        
        register_window = tk.Toplevel()
        register_window.transient(main_gui.window)
        
        def on_register_close():
            register_window.destroy()
            main_gui.resume_camera()
            
        register_window.protocol("WM_DELETE_WINDOW", on_register_close)
        
        def save_and_reload(name, surname, age, gender, images):
            try:
                # Save to database
                local_db.save_new_person(name, surname, age, gender, images)
                
                # Reload database
                new_db = local_db.load_face_database(recognizer.face_app)
                face_db.clear()
                face_db.extend(new_db)
                
                # Refresh main interface
                main_gui.face_db = face_db
                messagebox.showinfo("Success", "Person added successfully!")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save: {str(e)}")
                raise  # Propagate error back to RegisterWindow
            finally:
                on_register_close()
            
        gui.RegisterWindow(register_window, save_and_reload)
        register_window.grab_set()
    # Initialize main GUI
    
    main_gui = gui.FaceRecognitionGUI(
        recognize_func=recognize_wrapper,
        add_person_callback=add_person_handler,
        recognizer=recognizer,
        face_db=face_db
    )
    main_gui.run()

if __name__ == "__main__":
    main()
