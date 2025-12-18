import cv2
import numpy as np
import onnxruntime as ort
import random
import os
import time
import pyttsx3

class YoloV7ONNX:
    def __init__(self, weights_path, names_path, providers=['CPUExecutionProvider']):
        print(f"Loading weights from {weights_path}")
        self.session = ort.InferenceSession(weights_path, providers=providers)
        print(f"Loading class names from {names_path}")
        with open(names_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        print(f"Loaded {len(self.class_names)} class names: {self.class_names}")
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.class_names]
        print(f"Loaded {len(self.colors)} colors")
        self.engine = pyttsx3.init()
        print(f"Initialized TTS engine")
        self.detected_recently = {}  # avoid repeat chatter
        print("Initialized YoloV7ONNX detector")
    def speak(self, text):
        """Speak the given text using TTS engine."""
        if not text:
            print("[YoloV7ONNX] No text provided to speak.")
            return
        try:
            print(f"[YoloV7ONNX] Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[YoloV7ONNX] Error during speak: {e}")
    def get_available_cams(self, max_test=5):
        """Scan for available camera indices"""
        available = []
        for i in range(max_test):
            print(f"Trying to open camera index {i}")
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                print(f"Camera index {i} is opened")
                available.append(i)
            else:
                print(f"Camera index {i} is not opened")
        print(f"Available camera indexes: {available}")
        return available
    def load_classes(self, class_file):
        """Load class names from a file."""
        if not os.path.exists(class_file):
            print(f"Class file {class_file} does not exist.")
            return []
        with open(class_file, "r") as f:
            classes = [line.strip() for line in f.readlines()]
        return classes
    
    def load_model(self, onnx_path):
        """Load YOLOv7 model from ONNX file."""
        try:
            print(f"Loading model from {onnx_path}")
            return ort.InferenceSession(onnx_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            return None
    def run_onnx(self, image):
        """Run inference on the input image."""
        input_tensor, ratio, dwdh = self.preprocess(image)
        input_name = self.session.get_inputs()[0].name
        print(f"Running inference with input shape: {input_tensor.shape}")
        outputs = self.session.run(None, {input_name: input_tensor})[0]
        print(f"Inference completed with output shape: {outputs.shape}")
        return outputs, ratio, dwdh
    def letterbox(self, image, new_shape=(640, 640), stride=32):
        """Resize and pad the image to fit the model input."""
        shape = image.shape[:2]
        print(f"Original image shape: {shape}")
        ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        print(f"Resize ratio: {ratio}")  # ratio = new / old
        new_unpad = int(round(shape[1] * ratio)), int(round(shape[0] * ratio))
        print(f"New unpad shape: {new_unpad}")
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        print(f"dw, dh: {dw}, {dh}")
        dw /= 2
        dh /= 2
        print(f"Adjusted dw, dh: {dw}, {dh}")
        resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
        print(f"Resized shape: {resized.shape}")
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        print(f"Adjusted top, bottom, left, right: {top}, {bottom}, {left}, {right}")
        image = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
        print(f"Letterboxed image shape: {image.shape}")
        return image, ratio, (dw, dh)
    def encode_faces_from_frame(self, frame):
        """Extract face encodings from the frame."""
        import face_recognition
        print("Encoding faces from frame")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        print(f"Found {len(face_locations)} faces in the frame")
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        return encodings
    
    def preprocess(self, image, new_shape=(640, 640), stride=32):
        print("Preprocessing image")
        print(f"Image shape: {image.shape}")
        shape = image.shape[:2]
        print(f"Resizing to: {new_shape}")
        ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        print(f"Ratio: {ratio}")
        new_unpad = int(round(shape[1] * ratio)), int(round(shape[0] * ratio))
        print(f"new_unpad: {new_unpad}")
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        print(f"dw, dh: {dw}, {dh}")
        dw /= 2
        dh /= 2
        print(f"dw, dh: {dw}, {dh}")
        resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
        print(f"Resized shape: {resized.shape}")
        padded = cv2.copyMakeBorder(resized, int(round(dh - 0.1)), int(round(dh + 0.1)),
                                    int(round(dw - 0.1)), int(round(dw + 0.1)),
                                    cv2.BORDER_CONSTANT, value=(114, 114, 114))
        print(f"Padded shape: {padded.shape}")
        img = padded.transpose((2, 0, 1))[None]
        print(f"img shape: {img.shape}")
        return img.astype(np.float32) / 255.0, ratio, (dw, dh)

    def detect_from_webcams(self, conf_threshold=0.25):
        indexes = self.get_available_cams()
        if not indexes:
            self.speak("No camera detected, Sir.")
            return

        caps = [cv2.VideoCapture(i) for i in indexes]
        while True:
            for i, cap in enumerate(caps):
                ret, frame = cap.read()
                print(f"Read frame from camera {i}, ret={ret}")
                if not ret:
                    print(f"Skipping frame from camera {i} because it was empty.")
                    continue
                results, annotated = self.detect(frame, conf_threshold, draw=True, cam_id=i)

                print(f"Detected {len(results)} objects from camera {i}")
                for box, class_name, score in results:
                    print(f"  {class_name} {score:.2f} at {box}")

                cv2.putText(annotated, f"Cam {i}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.imshow(f"Jaicat | Camera {i}", annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        for cap in caps:
            cap.release()
        cv2.destroyAllWindows()

    def detect(self, image, conf_threshold=0.25, draw=False, cam_id=None):
        print("Starting detection")
        input_tensor, ratio, dwdh = self.preprocess(image)
        print("Preprocessing completed")
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_tensor})[0]
        print("Inference completed")

        results = []
        for batch_id, x0, y0, x1, y1, cls_id, score in outputs:
            if score < conf_threshold:
                print(f"Skipping detection with score {score:.2f} below threshold {conf_threshold}")
                continue
            box = np.array([x0, y0, x1, y1]) - np.array(dwdh * 2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            class_name = self.class_names[int(cls_id)]
            results.append((box, class_name, float(score)))
            print(f"Detected {class_name} with score {score:.2f} at {box}")

        if cam_id is not None:
            print(f"Handling voice feedback for camera {cam_id}")
            self._handle_voice_feedback(results, cam_id)

        annotated = self.draw_results(image.copy(), results) if draw else image
        print("Detection completed")
        return results, annotated

    def draw_results(self, image, results):
        for box, class_name, score in results:
            print(f"Drawing box for {class_name} with score {score:.2f} at {box}")
            idx = self.class_names.index(class_name)
            print(f"Class index: {idx}, color: {self.colors[idx]}")
            color = self.colors[idx]
            label = f"{class_name} {score:.2f}"
            print(f"Drawing label: {label}")
            cv2.rectangle(image, tuple(box[:2]), tuple(box[2:]), color, 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            print(f"Text size: {w}x{h}")
            cv2.rectangle(image, (box[0], box[1] - 20), (box[0] + w, box[1]), color, -1)
            print(f"Drawing label at {box[0]}, {box[1] - 5}")
            cv2.putText(image, label, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        print("Drawing completed")
        return image

    def _handle_voice_feedback(self, results, cam_id):
        now = time.time()
        print(f"Handling voice feedback at {now:.2f} for camera {cam_id}")
        for _, class_name, _ in results:
            recent = self.detected_recently.get((class_name, cam_id), 0)
            print(f"Detected {class_name} on camera {cam_id}, last seen at {recent:.2f}")
            if now - recent > 10:  # Speak once every 10 seconds per class/cam
                print(f"Speaking: I see a {class_name} on camera {cam_id}, Sir")
                self.speak(f"I see a {class_name} on camera {cam_id}, Sir")
                self.detected_recently[(class_name, cam_id)] = now

    def get_available_cams(self, max_test=5):
        """Scan for available camera indices"""
        available = []
        for i in range(max_test):
            print(f"Trying to open camera index {i}")
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                print(f"Camera index {i} is opened")
                available.append(i)
            else:
                print(f"Camera index {i} is not opened")
        print(f"Available camera indexes: {available}")
        return available
