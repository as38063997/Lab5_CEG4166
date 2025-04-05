import time, sys, tty, termios, curses
import cv2
from rotationSpeed_Graph import *
from PlotDataRobot import *
from picamera2 import PiCamera2
from HCSR04 import HCSR04
import threading
import RPi.GPIO as GPIO

# GPIO pin connected to the Servo
SERVO_PIN = 18  

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM for servo control (50Hz)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

#Function to capture keyboard input
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

#initialize the camera
camera = PiCamera2()
config = camera.create_preview_configuration(main={"size": (640, 480)})
camera.configure(config)

# Initialize Sonar Sensor (Using GPIO 7 for TRIG and GPIO 12 for ECHO)
sonar_sensor = HCSR04(trig=7, echo=12)

# Sonar Control HC-SR04
def set_servo_angle(angle):
    duty_cycle = (angle / 18.0) + 2
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)
    
def move_sonar_center():
    print("Moving sonar to center")
    set_servo_angle(90)
    

def move_sonar_right():
    print("Moving sonar to right")
    set_servo_angle(0)

def move_sonar_left():
    print("Moving sonar to left")
    set_servo_angle(180)


def sweep_sonar():
    print("Sweeping sonar...")
    for angle in range(0, 181, 30):  # Move from 0° to 180° in steps
        set_servo_angle(angle)
    for angle in range(180, -1, -30):  # Move back to 0°
        set_servo_angle(angle)
    print("Sonar sweep completed.")
    
def cleanup():
    print("Stopping Motors and Cleaning Up")
    Robot_stop()
    camera.stop()
    GPIO.cleanup()
    sys.exit()

# Initialize Plotting
left_encoder = 0
right_encoder = 0
plot = multiplePlots(left_encoder, right_encoder, samples=50, xmax=10)

def update_plot(i):
    plot.updateData()
    return plot.p011, plot.p012, plot.p021, plot.p022

ani = animation.FuncAnimation(plot.f0, update_plot, interval=100)

# List of student numbers
student_numbers = ["300201058", "300116948"]

# Function to display student numbers with flickering effect
def display_student_numbers():
    stdscr = curses.initscr()
    curses.curs_set(0)  # Hide cursor
    height, width = stdscr.getmaxyx()  # Get screen size

    try:
        for i in range(5):  # 5 seconds of display
            stdscr.clear()

            # Display student numbers (one per line)
            for idx, student in enumerate(student_numbers):
                x = width // 2 - len(student) // 2  # Center horizontally
                y = (height // 2 - len(student_numbers) // 2) + idx  # Center vertically
                stdscr.addstr(y, x, student, curses.A_BOLD)

            stdscr.refresh()
            time.sleep(0.5)  # Flicker on
            stdscr.clear()
            stdscr.refresh()
            time.sleep(0.5)  # Flicker off

    finally:
        curses.endwin()

# Run the function at the start of the program
display_student_numbers()

# Display menu
print("Enter the correct key to select an operation:")
print("w – Move forward | s – Move backward | d – Rotate right | a – Rotate left")
print("x – Stop wheels | c – Show camera | v – Exit camera")
print("k – Move sonar center | l – Move sonar right | j – Move sonar left | m – Sweep sonar")
print("p – Stop motors & Raspberry Pi")

while True:
    # Capture keyboard input
    char = getch()

    if char == "w":
        print("Moving Forward")
        Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
        Right_stop()

    elif char == "s":
        print("Moving Backward")
        Robot_reverse()
        time.sleep(.1)
        Robot_stop()

    elif char == "a":
        print("Rotating Left")
        Robot_left()
        time.sleep(.1)
        Robot_stop()

    elif char == "d":
        print("Rotating Right")
        Robot_right()
        time.sleep(.1)
        Robot_stop()

    elif char == "x":
        print("Stopping Robot")
        Robot_stop()

    elif char == "c":
        print("Starting Camera")
        camera.start()
        time.sleep(1)
        while True:
            frame = camera.capture_array()
            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('v'):
                break
        cv2.destroyAllWindows()

    elif char == "v":
        print("Stopping Camera")
        camera.stop()

    elif char == "k":
        print("Moving Sonar to Center")
        move_sonar_center()

    elif char == "l":
        print("Moving Sonar to Right")
        move_sonar_right()

    elif char == "j":
        print("Moving Sonar to Left")
        move_sonar_left()

    elif char == "m":
        print("Sweeping Sonar")
        sweep_sonar()

    elif char == "p":
        print("Stopping Motors and Shutting Down Raspberry Pi")
        cleanup()

    elif char == " ":
        print("Exiting Program")
        exit()

