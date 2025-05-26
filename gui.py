# gui.py
import cv2
import os
import tkinter as tk
from tkinter import ttk, messagebox, Button, Label
from PIL import Image, ImageTk

class FaceRecognitionGUI:
    def __init__(self, recognize_func, add_person_callback, recognizer, face_db):
        self.recognize_func = recognize_func
        self.add_person_callback = add_person_callback
        self.recognizer = recognizer
        self.face_db = face_db
        self.camera_active = True

        self.window = tk.Tk()
        self.window.title("Real-Time Face Recognition")
        
        # Initialize camera and get frame size
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if ret:
            h, w = frame.shape[:2]
            self.window.geometry(f"{w}x{h}")
        else:
            self.window.geometry("640x480")  # Fallback size

        # Video display (fills the window)
        self.video_label = Label(self.window)
        self.video_label.pack()

        # Add Person button (hidden initially)
        self.new_person_button = Button(
            self.window, 
            text="➕ Add Person", 
            command=self.add_person_callback,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        )
        # Position in bottom-right corner
        self.new_person_button.place(relx=0.95, rely=0.95, anchor="se")
        self.new_person_button.lower()

        self.update_video()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def update_video(self):
        if not self.camera_active:  # Check camera state
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Mirror and process frame
            frame = cv2.flip(frame, 1)
            frame, unknown_detected = self.recognize_func(frame, self.face_db)

            # Convert to Tkinter format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update display
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # Manage button visibility
            if unknown_detected:
                self.new_person_button.lift()
            else:
                self.new_person_button.lower()

        self.window.after(10, self.update_video)

    def pause_camera(self):
        self.camera_active = False
        self.cap.release()

    def resume_camera(self):
        self.camera_active = True
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        self.update_video()

    def close_window(self):
        self.camera_active = False
        self.cap.release()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

class RegisterWindow:
    def __init__(self, master, save_callback):
        self.master = master
        self.master.title("New Record")
        self.save_callback = save_callback
        self.image_count = 0
        self.max_images = 9
        self.images = []

        self.video_label = tk.Label(master)
        self.video_label.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

        self.example_img = Image.open("assets/face_pose_example.jpeg")  # açıklayıcı görsel
        self.example_img = self.example_img.resize((200, 200))
        self.example_photo = ImageTk.PhotoImage(self.example_img)
        tk.Label(master, image=self.example_photo).grid(row=0, column=1, padx=10, pady=10)

        self.name_var = tk.StringVar()
        self.surname_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()

        ttk.Label(master, text="Name:").grid(row=1, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.name_var).grid(row=1, column=2)

        ttk.Label(master, text="Surname:").grid(row=2, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.surname_var).grid(row=2, column=2)

        ttk.Label(master, text="Age:").grid(row=3, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.age_var).grid(row=3, column=2)

        ttk.Label(master, text="Gender:").grid(row=4, column=1, sticky="w")
        ttk.Combobox(master, textvariable=self.gender_var, values=["Male", "Female"]).grid(row=4, column=2)

        self.capture_btn = ttk.Button(master, text="📷Take Photo(SPACE)", command=self.capture_image)
        self.capture_btn.grid(row=5, column=1, columnspan=2)

        self.save_btn = ttk.Button(master, text="✅Save", command=self.save_data, state="disabled")
        self.save_btn.grid(row=6, column=1, columnspan=2, pady=10)

        master.bind("<space>", lambda e: self.capture_image())
        
        self.cap = None
        self.initialize_camera()
        self.update_frame()

    def initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Camera not available")
        except Exception as e:
            messagebox.showerror("Camera Error", str(e))
            self.master.destroy()


    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((320, 240))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.master.after(10, self.update_frame)

    def capture_image(self):
        if self.image_count < self.max_images:
            self.images.append(self.current_frame.copy())
            self.image_count += 1
            
            messagebox.showinfo("Info", f"{self.image_count}. photo saved.")
        else:
            messagebox.showwarning("Warning", f"You've already taken {self.image_count} photos.")
        
        # Update button state based on conditions
        if self.image_count == self.max_images and all([
            self.name_var.get(),
            self.surname_var.get(),
            self.age_var.get(),
            self.gender_var.get()]):
            self.save_btn.config(state="normal")
            
       
    def save_data(self):
        try:
            # Execute save callback
            self.save_callback(
                self.name_var.get(),
                self.surname_var.get(),
                self.age_var.get(),
                self.gender_var.get(),
                self.images
            )
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            # Keep window open for corrections
        finally:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.master.destroy()