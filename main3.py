import cv2
import serial
from ultralytics import YOLO

cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

model = YOLO('Model/tools_model.pt')

arduino = serial.Serial('COM5', 9600)  # Cambia 'COM5' por el puerto serial correcto de tu Arduino

frame_number = 1  # Inicializar el número de fotograma en 1

while True:
    ret, frame = cap.read()

    results = model.predict(frame, imgsz=640, conf=0.6)
    if len(results) != 0:
        for res in results:
            print('Tools detect')
            arduino.write(b'1')  # Envía el valor '1' al Arduino
            print("Comando enviado al Arduino")

        annotated_frames = results[0].plot()

    cv2.imshow('Tool detect', annotated_frames)
    t = cv2.waitKey(5)
    if t == 27:
        break

    frame_number += 1  # Incrementar el número de fotograma

cap.release()
cv2.destroyAllWindows()
