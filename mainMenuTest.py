
import tkinter as tk
from PIL import Image
from PIL import ImageTk
import numpy as np
import time
from picamera2 import Picamera2
from tkinter import IntVar
import terminatorlib as tlib
import random
from gpiozero import DistanceSensor

mesure = "N/A"
count = 0

def quit():
    root.destroy()




    

def update_frame():
    if checkCamera1.get() == 1 and camera is not None:
        # Camera ON
        frame = camera.capture_array()
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)

        camera_label.config(image=photo)
        camera_label.image = photo
    else:
        # Show solid black image of same size
        black_image = np.zeros((480, 640, 3), dtype=np.uint8)
        image = Image.fromarray(black_image)
        photo = ImageTk.PhotoImage(image)

        camera_label.config(image=photo)
        camera_label.image = photo

    

    root.after(30, update_frame)

# Main window
root = tk.Tk()
root.title("Robot GUI")
root.geometry("1280x960")

# Grid setup
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

checkCamera1 = IntVar(value=1)

# Frames
frame1 = tk.Frame(root, bg="lightblue")
frame1.grid(row=0, column=0, columnspan=2, sticky="nsew")

frame1.rowconfigure(1, weight=1)
frame1.columnconfigure(0, weight=1)



# Frame 1 content
label1 = tk.Label(frame1, text="Camera", font=("Arial", 20))
label1.grid(row=0, column=0, pady=10)

camera_label = tk.Label(frame1)
camera_label.grid(row=1, column=0, sticky="nsew")

checkButtonCamera = tk.Checkbutton(
    frame1,
    text="On/Off Camera",
    variable=checkCamera1,
    onvalue=1,
    offvalue=0,
    height=2,
    width=20
)
checkButtonCamera.grid(row=2, column=0, pady=10)





#quitter
button4 = tk.Button(frame1, text="Quit", command=quit, bg="red", fg="white")
button4.grid(row=3, column=0, pady=10, padx=10, sticky="sw")


# Initialize camera
camera = None
try:
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
    camera.start()
    time.sleep(1)
except IndexError:
    print("Warning: No camera found. Camera features will be disabled.")
    camera = None

# Start updating the frame
update_frame()

# Launch GUI
root.mainloop()
