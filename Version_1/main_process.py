from data_process import Horizontal
from flask import Flask, Response
from picamera2 import Picamera2
from angle_data import angle
import numpy as np
import serial
import joblib
import time
import cv2

model = joblib.load(r"/home/admin/received_frames/SVM.pkl")

h = Horizontal()
a = angle()
app = Flask(__name__)
class Process:
    def __init__(self):
        self.line = 20
        self.height = 480
        self.width = 640
        self.ang = 90
        self.ang_before = 90
        self.list = ['Forward', 'Turn right', 'Turn left', 'Turn right', 'Turn left']
        self.list_line = np.array([pixel for pixel in range(self.height - 40, self.height // 2, -self.line)])
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        time.sleep(2)
        
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (self.width, self.height)}
        )
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(1)

    def marking(self, frame):
        self.time_start = 0
        data = h.process_data(frame)
        if np.all(data == 0):
            self.ang = self.ang_before
        else:
            predict = int(model.predict([data])[0])
            self.ang = a.calculate_angle(data, predict)
        ang_int = int(round(self.ang))
        ang_int = max(0, min(255, ang_int))
        self.ser.write(bytes([ang_int]))
        
        x_r = data[10:20][data[10:20] != 0]
        x_l = data[0:10][data[0:10] != 0]
        n_points = min(len(x_r), len(x_l))
        x_r = x_r[:n_points]
        x_l = x_l[:n_points]
        x = (x_r + x_l) // 2
        y = self.list_line[:n_points]
        
        if np.all(data == 0):
            return frame
        else:
            for i in range(n_points):
                cv2.circle(frame, (int(x[i]),   int(y[i])), 3, (0, 0, 255), -1)
                cv2.circle(frame, (int(x_l[i]), int(y[i])), 3, (255, 0, 0), -1)
                cv2.circle(frame, (int(x_r[i]), int(y[i])), 3, (255, 0, 0), -1)
            
            cv2.putText(frame, f"Predict: {self.list[predict-1]}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, ( 0, 255, 0), 2)
            cv2.putText(frame, f"Angle: {self.ang:.2f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        self.ang_before = self.ang
        return frame
    
    def generate_frames(self):
        while True:
            time_start = time.time()
            frame = self.picam2.capture_array("main")
            frame = self.marking(frame)
            time_stop = time.time()
            average_time = (time_stop-time_start)*1000
            cv2.putText(frame, f"Resolution: {average_time:.2f} ms", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            

p = Process()
@app.route('/video')
def video():
    return Response(p.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("Starting Flask stream at http://0.0.0.0:5000/video")
    app.run(host="0.0.0.0", port=5000)
