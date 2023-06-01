import faceMouseDetector
import faceMouse

face_analyser = faceMouseDetector.FaceMouseDetector(path_to_blink_detector='models/blink_detector.h5')
faceMouse = faceMouse.Mouse(face_analyser)
faceMouse.run()

