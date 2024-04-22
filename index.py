# Libraries
from tkinter import *
from PIL import Image, ImageTk
import imutils
import cv2
import numpy as np
from ultralytics import YOLO
import math
import serial

# Cambios en la importación de serial
class Serial:
    def __init__(self, port, baudrate):
        pass

    def write(self, data):
        print(f"Data sent to Arduino: {data}")

def clean_lbl():
    # Clean
    lblimg.config(image='')
    lblimgtxt.config(image='')

def images(img, imgtxt):
    img = img
    imgtxt = imgtxt

    # Img Detect
    img = np.array(img, dtype="uint8")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = Image.fromarray(img)

    img_ = ImageTk.PhotoImage(image=img)
    lblimg.configure(image=img_)
    lblimg.image = img_

    # Img Text
    imgtxt = np.array(imgtxt, dtype="uint8")
    imgtxt = cv2.cvtColor(imgtxt, cv2.COLOR_BGR2RGB)
    imgtxt = Image.fromarray(imgtxt)

    img_txt = ImageTk.PhotoImage(image=imgtxt)
    lblimgtxt.configure(image=img_txt)
    lblimgtxt.image = img_txt

# Scanning Function
# Scanning Function
def Scanning(model1, model2):
    global img_metal, img_glass, img_plastic, img_carton, img_medical
    global img_metaltxt, img_glasstxt, img_plastictxt, img_cartontxt, img_medicaltxt, pantalla
    global lblimg, lblimgtxt

    # Interfaz
    lblimg = Label(pantalla)
    lblimg.place(x=75, y=260)

    lblimgtxt = Label(pantalla)
    lblimgtxt.place(x=995, y=310)
    detect = False

    # Read VideoCapture
    ret, frame = cap.read()
    frame_show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # True
    if ret == True:
        # Yolo | AntiSpoof
        results1 = model1(frame, stream=True, verbose=False)
        results2 = model2.predict(frame, imgsz=640, conf=0.6)

        for res in results1:
            # Box
            boxes = res.boxes
            for box in boxes:
                detect = True
                # Bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Error < 0
                if x1 < 0: x1 = 0
                if y1 < 0: y1 = 0
                if x2 < 0: x2 = 0
                if y2 < 0: y2 = 0

                # Class
                cls = int(box.cls[0])

                # Confidence
                conf = math.ceil(box.conf[0])

                # Send command to Arduino based on object detection
                if cls == 0:  # Organic object (manzana)
                    # Send command to Arduino to turn on green LED
                    arduino.write(b'0')
                    # Wait for response from Arduino
                    response = arduino.readline().decode().strip()
                    if response == '0':
                        print("Arduino confirmó recepción y procesamiento del comando '0'")
                    # Clasificacion
                    images(img_metal, img_metaltxt)

                elif cls == 1:  # Inorganic object
                    # Send command to Arduino to turn on red LED
                    arduino.write(b'1')
                    # Wait for response from Arduino
                    response = arduino.readline().decode().strip()
                    if response == '1':
                        print("Arduino confirmó recepción y procesamiento del comando '1'")
                    # Clasificacion
                    images(img_glass, img_glasstxt)

        if detect == False:
            # Clean
            clean_lbl()

        # Resize
        frame_show = imutils.resize(frame_show, width=640)

        # Convertimos el video
        im = Image.fromarray(frame_show)
        img = ImageTk.PhotoImage(image=im)

        # Mostramos en el GUI
        lblVideo.configure(image=img)
        lblVideo.image = img
        lblVideo.after(10, Scanning, model1, model2)

    else:
        cap.release()

# Main function
def ventana_principal():
    global cap, lblVideo, clsName, img_metal, img_glass, img_plastic, img_carton, img_medical
    global img_metaltxt, img_glasstxt, img_plastictxt, img_cartontxt, img_medicaltxt, pantalla, arduino

    # Ventana principal
    pantalla = Tk()
    pantalla.title("RECICLAJE INTELIGENTE")
    pantalla.geometry("1280x720")

    # Background
    imagenF = PhotoImage(file="setUp/Canva.png")
    background = Label(image=imagenF, text="Inicio")
    background.place(x=0, y=0, relwidth=1, relheight=1)

    # Modelos
    model1 = YOLO('Modelos/best.pt')
    model2 = YOLO('Model/tools_model.pt')

    # Clases
    clsName = ['Metal', 'Glass', 'Plastic', 'Carton', 'Medical']

    # Images
    img_metal = cv2.imread("setUp/metal.png")
    img_glass = cv2.imread("setUp/vidrio.png")
    img_plastic = cv2.imread("setUp/plastico.png")
    img_carton = cv2.imread("setUp/carton.png")
    img_medical = cv2.imread("setUp/medical.png")
    img_metaltxt = cv2.imread("setUp/metaltxt.png")
    img_glasstxt = cv2.imread("setUp/vidriotxt.png")
    img_plastictxt = cv2.imread("setUp/plasticotxt.png")
    img_cartontxt = cv2.imread("setUp/cartontxt.png")
    img_medicaltxt = cv2.imread("setUp/medicaltxt.png")

    # Video
    lblVideo = Label(pantalla)
    lblVideo.place(x=320, y=180)

    # Arduino setup
    arduino = serial.Serial(port='COM5', baudrate=9600)

    # Choose the camera
    cap = cv2.VideoCapture(1)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Llamamos a la función Scanning pasando los modelos como argumentos
    Scanning(model1, model2)

    # Run GUI
    pantalla.mainloop()

if __name__ == "__main__":
    ventana_principal()
