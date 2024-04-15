import cv2
from ultralytics import YOLO
import numpy as np
import pyttsx3
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load YOLO models
object_detection_model = YOLO("yolov8s.pt")  # For general object detection
pose_estimation_model = YOLO('yolov8n-pose.pt')  # For pose estimation

# Camera setup
#cap = cv2.VideoCapture(0)

# Video file setup
video_path = 'people.mp4'  # Replace with the path to your video file
cap = cv2.VideoCapture(video_path)


# Known physical width of a person's shoulders in inches (adjust as needed)
KNOWN_SHOULDER_WIDTH = 20  # Average shoulder width of an adult

# Define shoulder indices (ensure these are correct for your model's output)
LEFT_SHOULDER_INDEX = 6
RIGHT_SHOULDER_INDEX = 5

# Function to speak text asynchronously
def speak_async(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

# Function to estimate distance based on perceived width and known width
def estimate_distance(perceived_width, known_width):
    focal_length = 500  # Assumed focal length - this needs to be calibrated
    distance = (known_width * focal_length) / perceived_width
    return distance

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Object detection
    detection_results = object_detection_model(frame)
    boxes = detection_results[0].boxes.xyxy.tolist()
    class_ids = detection_results[0].boxes.cls.tolist()

    for box, class_id in zip(boxes, class_ids):
        x1, y1, x2, y2 = map(int, box)
        class_name = object_detection_model.names[class_id]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #cv2.putText(frame, f'{class_name}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        object_width_in_frame = x2 - x1

        # Estimate distance for all detected objects
        if class_name == 'person':
            pose_results = pose_estimation_model(frame)
            for result in pose_results:
                if len(result.keypoints.data) > 0:
                    keypoints_data = result.keypoints.data
                    if keypoints_data.shape[1] > max(LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX):
                        left_shoulder = keypoints_data[0][LEFT_SHOULDER_INDEX][:2].cpu().numpy()
                        right_shoulder = keypoints_data[0][RIGHT_SHOULDER_INDEX][:2].cpu().numpy()
                        cv2.line(frame, tuple(left_shoulder.astype(int)), tuple(right_shoulder.astype(int)), (255, 0, 0), 3)

                        shoulder_width = np.linalg.norm(right_shoulder - left_shoulder)
                        distance = estimate_distance(shoulder_width, KNOWN_SHOULDER_WIDTH)
                        cv2.putText(frame, f'{class_name}: {distance:.2f} cm', (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        if distance <= 50:
                            speak_async("Attention, person is near!")
        else:
            KNOWN_OBJECT_WIDTH = 5  # Example size for objects like cell phones
            distance = estimate_distance(object_width_in_frame, KNOWN_OBJECT_WIDTH)
            cv2.putText(frame, f'{class_name}: {distance:.2f} cm', (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if distance <= 50:
                speak_async(f"Attention, {class_name} is near!")

    cv2.imshow('Video Detections', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()