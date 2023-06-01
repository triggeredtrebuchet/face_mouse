import cv2
import dlib
import numpy as np
import os
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Input, Reshape, Dropout, Dense, Flatten


class FaceMouseDetector:
    def __init__(self, path_to_blink_detector=None):
        self.blink_detector = None
        if path_to_blink_detector is not None:
            self.load_blink_detector(path_to_blink_detector)

        face_shape_predictor_path = 'models/shape_predictor_68_face_landmarks.dat'
        self.face_detector = dlib.get_frontal_face_detector()
        self.face_shape_predictor = dlib.shape_predictor(face_shape_predictor_path)

    def assemble_dataset(self, dir_path):
        tensor_images = []
        labels = []
        # Traverse the directory and its subdirectories
        for root, dirs, files in os.walk(dir_path):
            # Iterate over the files in the current directory
            for file in files:
                if file.endswith('.jpg'):  # Filter only image files (change the extension if necessary)
                    label = os.path.basename(root)  # Use the subdirectory name as the label
                    image_path = os.path.join(root, file)  # Get the full path of the image
                    if label == "left_blink":
                        encoded_label = np.array([1, 0])
                    elif label == "right_blink":
                        encoded_label = np.array([0, 1])
                    elif label == "both_blink":
                        encoded_label = np.array([1, 1])
                    else:
                        encoded_label = np.array([0, 0])
                    image = cv2.imread(image_path)
                    tensor_image_points = self.preprocess_image(image)
                    # Append the image path and label to the list
                    if tensor_image_points is not None:
                        tensor_images.append(tensor_image_points)
                        labels.append(encoded_label)
        return np.array(tensor_images), np.array(labels)

    def preprocess_image(self, image):
        if image is None:
            return None
        face = self.face_detector(image)
        if len(face) < 1:
            return None
        landmarks = self.face_shape_predictor(image, face[0])
        x = []
        y = []
        for point in landmarks.parts():
            x.append(point.x)
            y.append(point.y)
        x = np.array(x)
        y = np.array(y)
        minx, maxx = min(x), max(x)
        miny, maxy = min(y), max(y)
        x = (x - (maxx + minx) / 2) / (
                (minx - maxx) / 2)  # Normalize landmarks - absolute position and size of face does not matter
        y = (y - (maxy + miny) / 2) / ((miny - maxy) / 2)
        x = x[17:48]
        y = y[17:48]
        return np.array([x, y])

    def create_new_blink_detector(self):
        self.blink_detector = Sequential([
            Input(shape=(2, 31,)),
            Flatten(),
            Dense(128, activation="relu"),
            Dropout(.25),
            Dense(64, activation="relu"),
            Dropout(.25),
            Dense(32, activation="relu"),
            Dense(16, activation="relu"),
            Dense(8, activation="relu"),
            Reshape((2, 4,)),
            Dense(2, activation="softmax"),
        ])
        optimizer = Adam(learning_rate=0.001, decay=0.0007)
        loss = SparseCategoricalCrossentropy(
            from_logits=False,
            reduction="auto",
            name="sparse_categorical_crossentropy",
        )

        self.blink_detector.compile(optimizer, loss, metrics='accuracy')

    def train(self, traindir_path, epochs=200, batch_size=12, valdir_path=None):
        validation_data = None
        validation_batch_size = None
        train_data = self.assemble_dataset(traindir_path)

        if valdir_path is not None:
            validation_data = self.assemble_dataset(valdir_path)
            validation_batch_size = 4

        self.blink_detector.fit(train_data[0], train_data[1],
                                epochs=epochs, batch_size=batch_size,
                                validation_data=validation_data,
                                validation_batch_size=validation_batch_size)

    def load_blink_detector(self, path_to_blink_detector):
        self.blink_detector = load_model(path_to_blink_detector)

    def detect(self, image):
        assert (self.blink_detector is not None)
        points = self.preprocess_image(image)
        if points is not None:
            return self.blink_detector.predict(np.array([points]))[0, :, 1], points[:, 16]
