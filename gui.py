import cv2
import tkinter as tk
from tkinter import ttk, messagebox, Button, Label
from PIL import Image, ImageTk

class FaceRecognitionGUI:
    """Main application GUI for real-time face recognition"""
    def __init__(self, recognize_func, add_person_callback, recognizer, face_db):
        # Store recognition components and database
        self.recognize_func = recognize_func
        self.add_person_callback = add_person_callback
        self.recognizer = recognizer
        self.face_db = face_db
        self.camera_active = True  # Camera state flag

        # Create main application window
        self.window = tk.Tk()
        self.window.title("Real-Time Face Recognition")
        
        # Initialize camera and set window size
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if ret:
            # Set window size to match camera resolution
            h, w = frame.shape[:2]
            self.window.geometry(f"{w}x{h}")
        else:
            # Fallback size if camera not available
            self.window.geometry("640x480")

        # Create video display label
        self.video_label = Label(self.window)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Create "Add Person" button
        self.new_person_button = Button(
            self.window, 
            text="➕ Add Person", 
            command=self.add_person_callback,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        )
        # Position button in bottom-right corner
        self.new_person_button.place(relx=0.95, rely=0.95, anchor="se")
        self.new_person_button.lower()  # Hide initially
        
        # Start video processing loop
        self.update_video()
        # Set close handler to release resources
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def update_video(self):
        """Continuously update video feed with face recognition"""
        if not self.camera_active:
            return
            
        # Read frame from camera
        ret, frame = self.cap.read()
        if ret:
            # Mirror image for natural display
            frame = cv2.flip(frame, 1)
            # Process frame with recognition function
            frame, unknown_detected = self.recognize_func(frame, self.face_db)

            # Convert frame to Tkinter-compatible format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update display with new frame
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # Show/hide "Add Person" button based on detection
            if unknown_detected:
                self.new_person_button.lift()
            else:
                self.new_person_button.lower()

        # Schedule next frame update
        self.window.after(10, self.update_video)

    def pause_camera(self):
        """Pause camera feed and release resources"""
        self.camera_active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def resume_camera(self):
        """Resume camera feed after pause"""
        self.camera_active = True
        # Reinitialize camera
        self.cap = cv2.VideoCapture(0)
        # Restart video processing
        self.update_video()

    def close_window(self):
        """Clean up resources when closing application"""
        self.camera_active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

    def run(self):
        """Start the main application loop"""
        self.window.mainloop()

class RegisterWindow:
    """Window for registering new people in the system"""
    def __init__(self, master, save_callback):
        # Store reference to parent window and save handler
        self.master = master
        self.save_callback = save_callback
        
        # Initialize registration state
        self.image_count = 0
        self.max_images = 9
        self.images = []

        # Create video display for camera feed
        self.video_label = tk.Label(master)
        self.video_label.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

        # Load and display example pose image
        try:
            self.example_img = Image.open("assets/face_pose_example.jpeg")
            self.example_img = self.example_img.resize((200, 200))
            self.example_photo = ImageTk.PhotoImage(self.example_img)
            tk.Label(master, image=self.example_photo).grid(row=0, column=1, padx=10, pady=10)
        except Exception:
            # Handle missing example image gracefully
            pass

        # Create input fields for person details
        self.name_var = tk.StringVar()
        self.surname_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()

        # Name field
        ttk.Label(master, text="Name:").grid(row=1, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.name_var).grid(row=1, column=2)

        # Surname field
        ttk.Label(master, text="Surname:").grid(row=2, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.surname_var).grid(row=2, column=2)

        # Age field
        ttk.Label(master, text="Age:").grid(row=3, column=1, sticky="w")
        ttk.Entry(master, textvariable=self.age_var).grid(row=3, column=2)

        # Gender selection
        ttk.Label(master, text="Gender:").grid(row=4, column=1, sticky="w")
        ttk.Combobox(master, textvariable=self.gender_var, 
                     values=["Male", "Female"]).grid(row=4, column=2)

        # Capture button
        self.capture_btn = ttk.Button(master, text="📷Take Photo(SPACE)", 
                                     command=self.capture_image)
        self.capture_btn.grid(row=5, column=1, columnspan=2)

        # Save button (disabled until all requirements met)
        self.save_btn = ttk.Button(master, text="✅Save", 
                                  command=self.save_data, state="disabled")
        self.save_btn.grid(row=6, column=1, columnspan=2, pady=10)

        # Bind space key to capture function
        master.bind("<space>", lambda e: self.capture_image())
        
        # Initialize camera and start video feed
        self.cap = None
        self.initialize_camera()
        self.update_frame()

    def initialize_camera(self):
        """Set up camera for registration window"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap or not self.cap.isOpened():
                raise RuntimeError("Camera not available")
        except Exception as e:
            messagebox.showerror("Camera Error", str(e))
            self.master.destroy()

    def update_frame(self):
        """Continuously update registration camera feed"""
        if not self.cap or not self.cap.isOpened():
            return
            
        # Read frame from camera
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            # Convert to RGB format for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            # Resize for UI consistency
            img = img.resize((320, 240))
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update display
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            
        # Schedule next frame update
        self.master.after(10, self.update_frame)

    def capture_image(self):
        """Capture and store current frame"""
        if self.image_count < self.max_images:
            # Save current frame
            self.images.append(self.current_frame.copy())
            self.image_count += 1
            messagebox.showinfo("Info", f"{self.image_count}/9 photos captured")
        else:
            messagebox.showwarning("Warning", "Maximum 9 photos reached")
        
        # Enable save button if all requirements met
        if (self.image_count >= self.max_images and 
            self.name_var.get() and 
            self.surname_var.get() and 
            self.age_var.get() and 
            self.gender_var.get()):
            self.save_btn.config(state="normal")

    def save_data(self):
        """Save new person data and close window"""
        try:
            # Pass data to save callback
            self.save_callback(
                self.name_var.get(),
                self.surname_var.get(),
                self.age_var.get(),
                self.gender_var.get(),
                self.images
            )
        except Exception as e:
            # Display error but keep window open
            messagebox.showerror("Save Error", str(e))
        finally:
            # Always release camera and close window
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.master.destroy()