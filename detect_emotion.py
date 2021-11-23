from __future__ import print_function
import tkinter as tk
from tkinter import *
import cv2 as cv
from PIL import Image, ImageTk
import os
from deepface import DeepFace
import shared
from shared import *
from tkinter import messagebox

class Detect_Emotion(tk.Toplevel):
    def __init__(self, face_cascade_name, camera_device, root_dir):
        super().__init__()
        self.title("Let's detect your emotion ><")

        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        w = 800
        h = 600
        self.geometry("{}x{}+{}+{}".format(w, h + 20, (screenWidth - w)//2, (screenHeight - h)//2))  # set window size
        self.configure(bg="sky blue", cursor="arrow")

        self.frame0 = tk.Frame(self,  width=800, height=300, bg="sky blue")    
        self.frame1 = tk.Frame(self, bg="sky blue")
        self.frames = [self.frame0, self.frame1]
        self.face_cascade = cv.CascadeClassifier()
        if not self.face_cascade.load(cv.samples.findFile(face_cascade_name)):
            print('--(!)Error loading face cascade')
            exit(0)
        
        self.camera = cv.VideoCapture(camera_device)
        if not self.camera.isOpened:
            print('--(!)Error opening video capture')
            exit(0)   
        self.root_dir = root_dir
        self.create_widgets()
        self.video_loop()

    def create_widgets(self):
        """ create a widget
        """
        self.Image_Label = Label(self.frames[0], width = 780, height = 500)
        self.DetectBtn = Button(self.frames[1],  activebackground = 'Salmon', text = "Detect Emotion", font = shared.FONT, command=self.detect_go)  
        self.ExitBtn = Button(self.frames[1], bg = 'sky blue', text = "Exit", font = shared.FONT, command=self.exit)  
        self.Result_Label = Label(self.frames[1], fg = 'steel blue', bg = 'sky blue', text = "Press Detect", font = shared.MAIN_FONT)
        self.Image_Label.pack(padx=10, pady=10)
        self.DetectBtn.pack(padx=5, pady=5, side = tk.LEFT)
        self.ExitBtn.pack(padx=5, pady=5, side = tk.LEFT)
        self.Result_Label.pack(padx=5, pady=5, side = tk.RIGHT)

        self.frame0.pack(side=tk.TOP, fill=tk.BOTH)    
        self.frame1.pack(side=tk.TOP, fill=tk.BOTH )  

    def video_loop(self):
        success, self.img = self.camera.read()  
        if self.img is None:
            # print('--(!) No captured frame -- Break!')
            messagebox.showwarning('No camera', '--(!) No captured frame -- Break!')
            self.exit()
        if success:
            cv.waitKey(100)
            self.cvimage = cv.cvtColor(self.img, cv.COLOR_BGR2RGBA)  
            current_image = Image.fromarray(self.cvimage)
            imgtk = ImageTk.PhotoImage(image=current_image)
            self.Image_Label.imgtk = imgtk
            self.Image_Label.config(image=imgtk)
            self.update()
            self.after(1, self.video_loop)
        

    def save_img(self, filename):
        cv.imwrite(filename, img=self.sub_image)
        print("Picture {} saved!".format(filename))
        
        

    def detect_go(self):
        self.DetectBtn["state"] = tk.DISABLED
        frame_gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        frame_gray = cv.equalizeHist(frame_gray)
        #-- Detect faces
        faces = self.face_cascade.detectMultiScale(frame_gray)
        for (x,y,w,h) in faces:
            x_out, y_out, w_out, h_out = x, y, w, h
        self.sub_image = self.img[y_out : y_out + h_out, x_out : x_out + w_out]
        filename = os.path.join(self.root_dir, "tmp.jpg")
        self.save_img(filename)
        print_message("Analyzing emotion~~")
        result = self.predict_emotion(img_path = filename)
        result = "{}{}".format(result[0].upper(), result[1:])
        self.Result_Label["text"] = result
        self.DetectBtn["state"] = "normal"

    def predict_emotion(self, img_path, actions = ['emotion']):
        result = DeepFace.analyze(img_path, actions)
        print("Emotion: {}".format(result["dominant_emotion"]))
        return result["dominant_emotion"]
    
    def exit(self):
        self.camera.release()
        cv.destroyAllWindows()
        self.destroy()