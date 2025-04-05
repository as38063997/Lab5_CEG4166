import time
import pigpio
import RPi.GPIO as GPIO
from Motor_control import RobotControl 
from HCSR04 import HCSR04

# Scan angles: right, center, left
SCAN_ANGLES = [10, 80, 150]
DISTANCE_THRESHOLD = 20  # cm

class Servo:
    def __init__(self, pin):
        self.pi = pigpio.pi()
        self.pin = pin
        self.pi.set_mode(pin, pigpio.OUTPUT)

    def set_angle(self, angle):
        pulse_width = 500 + (angle / 180.0) * 2000  # Range: 500–2500 µs
        self.pi.set_servo_pulsewidth(self.pin, pulse_width)

    def center(self):
        self.set_angle(80)

    def stop(self):
        self.pi.set_servo_pulsewidth(self.pin, 0)
        self.pi.stop()

def scan_directions(sensor, servo):
    # Rotate the servo to scan the environment and return averaged distances.
    distances = []
    for angle in SCAN_ANGLES:
        servo.set_angle(angle)
        time.sleep(0.3)  # Allow servo to settle
        # Take multiple readings and compute the average
        readings = [sensor.measure(1, "cm") for _ in range(3)]
        avg_distance = sum(readings) / len(readings)
        print(f"Angle {angle}°: Readings: {readings} → Avg: {avg_distance:.2f} cm")
        distances.append(avg_distance)
    # Reset servo to face forward
    servo.set_angle(80)
    return distances

def decide_direction(distances):
    """
    Choose the direction with the maximum distance.
    If all readings are too short, return 'back'.
    """
    if max(distances) < DISTANCE_THRESHOLD:
        return "back"
    mapping = {0: "right", 1: "forward", 2: "left"}
    best_index = distances.index(max(distances))
    return mapping[best_index]

def main():
    print("Starting navigation system...")

    # Set up GPIO for the HC-SR04 sensor (and any other GPIO pins)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # Pin assignments
    trig_pin = 7
    echo_pin = 12
    servo_pin = 25  # This is the pin used to control the servo

    # Initialize sensor, servo, and robot control
    sensor = HCSR04(trig=trig_pin, echo=echo_pin)
    servo = Servo(servo_pin)
    pi = pigpio.pi()
    robot = RobotControl(pi)
    
    # Ensure servo is initially centered
    servo.set_angle(80)
    
    try:
        while True:
            # Check the distance straight ahead (sensor should be pointing forward)
            front_distance = sensor.measure(samples=3, unit="cm")
            print(f"Front distance: {front_distance} cm")
            
            if front_distance > DISTANCE_THRESHOLD:
                # Path is clear, continue forward
                robot.move_forward()
            else:
                # Obstacle detected, stop and scan for an alternative route
                robot.stop_robot()
                print("Obstacle detected! Scanning for alternative paths...")
                distances = scan_directions(sensor, servo)
                chosen_direction = decide_direction(distances)
                print(f"Decided direction: {chosen_direction}")
                
                # Execute a turn based on the chosen direction
                if chosen_direction == "left":
                    robot.rotate_left()
                elif chosen_direction == "right":
                    robot.rotate_right()
                elif chosen_direction == "back":
                    robot.move_backward()
                    time.sleep(0.5)
                    robot.rotate_left()
                    
            # Small delay for stability
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        print("Navigation stopped by user.")
    
    finally:
        robot.stop_robot()
        servo.stop()
        pi.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
