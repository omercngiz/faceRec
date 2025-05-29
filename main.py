import local_db
import gui
import tkinter as tk
from tkinter import messagebox
from recognize import Recognizer

def main():
    """Main application entry point that sets up the face recognition system"""
    # Initialize the face recognition engine
    recognizer = Recognizer()
    
    # Load face database from storage
    face_db = local_db.load_face_database(recognizer.face_app)
    
    def recognize_wrapper(frame, db):
        """Wrapper function for face recognition processing"""
        return recognizer.recognize_faces(frame, db)

    def add_person_handler():
        """Handles new person registration workflow"""
        # Pause main camera feed during registration
        main_gui.pause_camera()
        
        # Create registration window as child of main GUI
        register_window = tk.Toplevel()
        register_window.transient(main_gui.window)
        
        def on_register_close():
            """Cleanup handler when registration window closes"""
            register_window.destroy()
            # Resume main camera feed
            main_gui.resume_camera()
            
        # Ensure proper cleanup on window close
        register_window.protocol("WM_DELETE_WINDOW", on_register_close)
        
        def save_and_reload(name, surname, age, gender, images):
            """Saves new person data and refreshes recognition system"""
            try:
                # Save new person to database
                local_db.save_new_person(name, surname, age, gender, images)
                
                # Reload face database with new entry
                new_db = local_db.load_face_database(recognizer.face_app)
                face_db.clear()
                face_db.extend(new_db)
                
                # Update recognition system with new database
                main_gui.face_db = face_db
                messagebox.showinfo("Success", "Person added successfully!")
                
            except Exception as e:
                # Handle save errors
                messagebox.showerror("Save Error", f"Failed to save: {str(e)}")
                raise  # Propagate error to registration window
            finally:
                # Always close registration window
                on_register_close()
            
        # Initialize registration interface
        gui.RegisterWindow(register_window, save_and_reload)
        # Make window modal (blocks main window interaction)
        register_window.grab_set()
    
    # Initialize and start main application GUI
    main_gui = gui.FaceRecognitionGUI(
        recognize_func=recognize_wrapper,
        add_person_callback=add_person_handler,
        recognizer=recognizer,
        face_db=face_db
    )
    main_gui.run()

if __name__ == "__main__":
    # Start application execution
    main()