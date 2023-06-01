from tkinter import *
from PIL import Image, ImageTk
import cv2 as cv


class OptionWindow:
    def __init__(self, mouse):
        self.mouse = mouse
        self.root = Tk()
        self.root.title('Face Mouse')
        self.root.geometry('940x640')
        self.root.resizable(False, False)

        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Unable to read camera feed")

        self.camera_frame = LabelFrame(self.root, width=640, height=640)
        self.camera_frame.pack(side=LEFT)
        self.camera_label = Label(self.camera_frame, width=640, height=640)
        self.camera_label.pack()

        self.mouse_options = PanedWindow(orient=VERTICAL)
        self.mouse_options.pack(side=RIGHT)

        self.left_click_sens_var = DoubleVar()
        self.left_click_sens = Scale(self.mouse_options, from_=0.8, to=1, orient=HORIZONTAL, resolution=0.005,
                                     label="left_click_sensitivity", length=200, variable=self.left_click_sens_var,
                                     command=lambda x: self.mouse.set_left_click_sens(self.left_click_sens_var.get())) # 'x' is for error prevention
        self.left_click_sens.set(0.9)
        self.left_click_sens.pack(padx=40, pady=5)

        self.right_click_sens_var = DoubleVar()
        self.right_click_sens = Scale(self.mouse_options, from_=0.8, to=1, orient=HORIZONTAL, resolution=0.005,
                                      label="right_click_sensitivity", length=200, variable=self.right_click_sens_var,
                                      command=lambda x: self.mouse.set_right_click_sens(self.right_click_sens_var.get()))
        self.right_click_sens.set(0.9)
        self.right_click_sens.pack(padx=40, pady=5)

        self.mouse_horizontal_sens_var = DoubleVar()
        self.mouse_horizontal_sens = Scale(self.mouse_options, from_=-150, to=150, orient=HORIZONTAL,
                                           label="mouse_horizontal_sensitivity", length=200,
                                           variable=self.mouse_horizontal_sens_var,
                                           command=lambda x: self.mouse.set_mouse_horizontal_sens(self.mouse_horizontal_sens_var.get()))
        self.mouse_horizontal_sens.set(40)
        self.mouse_horizontal_sens.pack(padx=40, pady=5)

        self.mouse_vertical_sens_var = DoubleVar()
        self.mouse_vertical_sens = Scale(self.mouse_options, from_=-150, to=150, orient=HORIZONTAL,
                                         label="mouse_vertical_sensitivity", length=200,
                                         variable=self.mouse_vertical_sens_var,
                                         command=lambda x: self.mouse.set_mouse_vertical_sens(self.mouse_vertical_sens_var.get()))
        self.mouse_vertical_sens.set(-100)
        self.mouse_vertical_sens.pack(padx=40, pady=5)

        self.nose_vertical_pos_var = DoubleVar()
        self.nose_vertical_pos = Scale(self.mouse_options, from_=-0.2, to=0.2, orient=HORIZONTAL, resolution=0.005,
                                       label="nose_vertical_position", length=200, variable=self.nose_vertical_pos_var,
                                       command=lambda x: self.mouse.set_nose_vertical_pos(self.nose_vertical_pos_var.get()))
        self.nose_vertical_pos.set(0)
        self.nose_vertical_pos.pack(padx=40, pady=5)

        self.nose_horizontal_pos_var = DoubleVar()
        self.nose_horizontal_pos = Scale(self.mouse_options, from_=-0.2, to=0.2, orient=HORIZONTAL, resolution=0.005,
                                         label="nose_horizontal_position", length=200,
                                         variable=self.nose_horizontal_pos_var,
                                         command=lambda x: self.mouse.set_nose_horizontal_pos(self.nose_horizontal_pos_var.get()))
        self.nose_horizontal_pos.set(0)
        self.nose_horizontal_pos.pack(padx=40, pady=5)

        self.idle_movement_range_var = DoubleVar()
        self.idle_movement_range = Scale(self.mouse_options, from_=0, to=0.05, orient=HORIZONTAL, resolution=0.001,
                                         label="idle_movement_range", length=200, variable=self.idle_movement_range_var,
                                         command=lambda x: self.mouse.set_idle_movement_range(self.idle_movement_range_var.get()))
        self.idle_movement_range.set(0.0)
        self.idle_movement_range.pack(padx=40, pady=5)

        self.acceleration_effect_var = DoubleVar()
        self.acceleration_effect = Scale(self.mouse_options, from_=0, to=3, orient=HORIZONTAL, resolution=0.1,
                                         label="acceleration_effect", length=200, variable=self.acceleration_effect_var,
                                         command=lambda x: self.mouse.set_acceleration_effect(self.acceleration_effect_var.get()))
        self.acceleration_effect.set(1.5)
        self.acceleration_effect.pack(padx=40, pady=5)

        self.mouse_disp = PanedWindow(self.mouse_options, orient=HORIZONTAL)
        self.mouse_disp.pack(fill=BOTH, expand=True)

        self.left_click_disp = Button(self.mouse_disp, height=19, width=19, command=self.click_left, text="Left blink")
        self.mouse_disp.add(self.left_click_disp)

        self.right_click_disp = Button(self.mouse_disp, height=19, width=19, command=self.click_right,
                                       text="Right blink")
        self.mouse_disp.add(self.right_click_disp)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_window)

    def exit_window(self):
        self.mouse.shouldWork = False
        self.cap.release()
        cv.destroyAllWindows()
        self.root.destroy()
        self.root.quit()

    def click_left(self):
        self.left_click_disp.config(bg='red')
        self.left_click_disp.after(300, lambda: self.left_click_disp.config(bg='white'))

    def click_right(self):
        self.right_click_disp.config(bg='red')
        self.right_click_disp.after(300, lambda: self.right_click_disp.config(bg='white'))

    def update_camera(self, image):
        img = ImageTk.PhotoImage(Image.fromarray(image))
        self.camera_label['image'] = img
        self.root.update()
