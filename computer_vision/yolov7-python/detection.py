import cv2
import numpy as np
import onnxruntime as ort
import random
import os
import time
import pyttsx3

class YoloV7ONNX:
    def __init__(self, weights_path, names_path, providers=['CPUExecutionProvider']):
        self.session = ort.InferenceSession(weights_path, providers=providers)
        with open(names_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.class_names]
        self.engine = pyttsx3.init()
        self.detected_recently = {}  # avoid repeat chatter

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def preprocess(self, image, new_shape=(640, 640), stride=32):
        shape = image.shape[:2]
        ratio = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        new_unpad = int(round(shape[1] * ratio)), int(round(shape[0] * ratio))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2
        resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
        padded = cv2.copyMakeBorder(resized, int(round(dh - 0.1)), int(round(dh + 0.1)),
                                    int(round(dw - 0.1)), int(round(dw + 0.1)),
                                    cv2.BORDER_CONSTANT, value=(114, 114, 114))
        img = padded.transpose((2, 0, 1))[None]
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
                if not ret:
                    continue
                results, annotated = self.detect(frame, conf_threshold, draw=True, cam_id=i)

                cv2.putText(annotated, f"Cam {i}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.imshow(f"Jaicat | Camera {i}", annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        for cap in caps:
            cap.release()
        cv2.destroyAllWindows()

    def detect(self, image, conf_threshold=0.25, draw=False, cam_id=None):
        input_tensor, ratio, dwdh = self.preprocess(image)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_tensor})[0]

        results = []
        for batch_id, x0, y0, x1, y1, cls_id, score in outputs:
            if score < conf_threshold:
                continue
            box = np.array([x0, y0, x1, y1]) - np.array(dwdh * 2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            class_name = self.class_names[int(cls_id)]
            results.append((box, class_name, float(score)))

        if cam_id is not None:
            self._handle_voice_feedback(results, cam_id)

        annotated = self.draw_results(image.copy(), results) if draw else image
        return results, annotated

    def draw_results(self, image, results):
        for box, class_name, score in results:
            idx = self.class_names.index(class_name)
            color = self.colors[idx]
            label = f"{class_name} {score:.2f}"
            cv2.rectangle(image, tuple(box[:2]), tuple(box[2:]), color, 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(image, (box[0], box[1] - 20), (box[0] + w, box[1]), color, -1)
            cv2.putText(image, label, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        return image

    def _handle_voice_feedback(self, results, cam_id):
        now = time.time()
        for _, class_name, _ in results:
            recent = self.detected_recently.get((class_name, cam_id), 0)
            if now - recent > 10:  # Speak once every 10 seconds per class/cam
                self.speak(f"I see a {class_name} on camera {cam_id}, Sir 💁‍♀️")
                self.detected_recently[(class_name, cam_id)] = now

    def get_available_cams(self, max_test=5):
        """Scan for available camera indices"""
        return [i for i in range(max_test) if cv2.VideoCapture(i).read()[0]]