import cv2
import pyautogui
import threading
import optionWindow
import win32api, win32con
import time


class Mouse:
    def __init__(self, face_mouse_detector, left_click_sens=0.96, right_click_sens=0.96,
                 mouse_vertical_sens=-100, mouse_horizontal_sens=40,
                 nose_vertical_pos=+0.00, nose_horizontal_pos=0,
                 idle_movement_range=0.035, acceleration_effect=1.5):
        self.cap = cv2.VideoCapture(1)
        self.faceMouseDetector = face_mouse_detector
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        self.left_click_sensitivity = left_click_sens
        self.right_click_sensitivity = right_click_sens
        self.mouse_vertical_sensitivity = mouse_vertical_sens
        self.mouse_horizontal_sensitivity = mouse_horizontal_sens
        self.nose_horizontal_pos = nose_horizontal_pos
        self.nose_vertical_pos = nose_vertical_pos
        self.idle_movement_range = idle_movement_range
        self.acceleration_effect = acceleration_effect

        self.vertical_velocity = 0.0
        self.horizontal_velocity = 0.0

        self.window = optionWindow.OptionWindow(self)

        self.shouldWork = True
        pyautogui.FAILSAFE = False

    def camera_read_and_analyse(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.window.update_camera(frame)
            return self.faceMouseDetector.detect(frame)

    def run(self):
        mover = threading.Thread(target=self.mouse_movement)
        mover.start()
        while self.shouldWork:
            ans = self.camera_read_and_analyse()
            if ans is None:
                continue
            blink, move = ans
            if blink[0] > self.left_click_sensitivity:
                # pyautogui.click()
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.02)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                self.window.click_left()
            if blink[1] > self.right_click_sensitivity:
                pyautogui.click(button='right')
                self.window.click_right()

            if abs(move[0]) > self.idle_movement_range:
                self.horizontal_velocity = self.mouse_horizontal_sensitivity * (move[0] - self.nose_horizontal_pos)
                self.horizontal_velocity *= abs(self.horizontal_velocity) ** self.acceleration_effect
                # This creates square relation between movement of the face and velocity of the cursor - helps
            else:
                self.horizontal_velocity = 0
            if abs(move[1]) > self.idle_movement_range:
                self.vertical_velocity = self.mouse_vertical_sensitivity * (move[1] - self.nose_vertical_pos)
                self.vertical_velocity *= abs(self.vertical_velocity) ** self.acceleration_effect
                # This creates square relation between movement of the face and velocity of the cursor - helps
            else:
                self.vertical_velocity = 0

        self.kill(mover)
        self.window.exit_window()

    def mouse_movement(self):
        start_time = cv2.getTickCount()
        end_time = cv2.getTickCount()
        while self.shouldWork:
            delta_time = (end_time - start_time) / cv2.getTickFrequency()
            start_time = cv2.getTickCount()
            pyautogui.move(int(self.horizontal_velocity * delta_time), int(self.vertical_velocity * delta_time))
            end_time = cv2.getTickCount()

    def kill(self, mover):
        self.cap.release()
        cv2.destroyAllWindows()
        mover.join()

    #################################
    ############ Setters ############
    #################################

    '''left_click_sens = 0.96, right_click_sens = 0.96,
    mouse_vertical_sens = -100, mouse_horizontal_sens = 40,
    nose_vertical_pos = +0.00, nose_horizontal_pos = 0,
    idle_movement_range = 0.035, acceleration_effect = 1.5'''

    def set_left_click_sens(self, val):
        self.left_click_sensitivity = val

    def set_right_click_sens(self, val):
        self.right_click_sensitivity = val

    def set_mouse_vertical_sens(self, val):
        self.mouse_vertical_sensitivity = val

    def set_mouse_horizontal_sens(self, val):
        self.mouse_horizontal_sensitivity = val

    def set_nose_vertical_pos(self, val):
        self.nose_vertical_pos = val

    def set_nose_horizontal_pos(self, val):
        self.nose_horizontal_pos = val

    def set_idle_movement_range(self, val):
        self.idle_movement_range = val

    def set_acceleration_effect(self, val):
        self.acceleration_effect = val
