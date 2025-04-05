import time
import pigpio

class Servo_write:
    """
    Class to control a servo/motor using PWM signals.
    """
    def __init__(self, pi, gpio, min_pw=1280, max_pw=1720, min_speed=-200, max_speed=200):
        self.pi = pi
        self.gpio = gpio
        self.min_pw = min_pw
        self.max_pw = max_pw
        self.min_speed = min_speed
        self.max_speed = max_speed

        # Calculate the mapping slope and offset
        self.slope = (self.max_pw - self.min_pw) / (self.max_speed - self.min_speed)
        self.offset = (self.min_pw + self.max_pw) / 2

        # Initialize the servo as stopped
        self.stop()

    def calc_pw_speed(self, speed):
        """
        Convert speed (-200 to 200) into a PWM pulse width (1280 to 1720).
        """
        speed = max(self.min_speed, min(self.max_speed, speed))
        pulse_width = self.slope * speed + self.offset
        return int(pulse_width)

    def set_speed(self, speed):
        """
        Set the motor speed using PWM.
        """
        calculated_pw = self.calc_pw_speed(speed)
        self.set_pw(calculated_pw)

    def set_pw(self, pulse_width):
        """
        Set the servo/motor to a specific pulse width.
        """
        pulse_width = max(self.min_pw, min(self.max_pw, pulse_width))
        self.pi.set_servo_pulsewidth(self.gpio, pulse_width)

    def stop(self):
        """
        Stop the motor by setting it to the neutral pulse width.
        """
        self.set_pw((self.min_pw + self.max_pw) / 2)

class RobotControl:
    def __init__(self, pi):
        self.pi = pi
        self.left_motor = Servo_write(pi, gpio=23, min_pw=1280, max_pw=1720, min_speed=-200, max_speed=200)
        self.right_motor = Servo_write(pi, gpio=24, min_pw=1280, max_pw=1720, min_speed=-200, max_speed=200)

    def display_message(self, message):
        """
        Display a message in the terminal. For multi-word messages, split the lines.
        """
        words = message.split()
        if len(words) == 2:
            print(f"{words[0]}\n{words[1]}")
        else:
            print(message)

    def move_forward(self):
        self.display_message("moving forward")
        self.left_motor.set_speed(100)
        self.right_motor.set_speed(-100)

    def move_backward(self):
        self.display_message("moving backward")
        self.left_motor.set_speed(-100)
        self.right_motor.set_speed(100)

    def rotate_left(self):
        self.display_message("rotating left")
        self.left_motor.set_speed(-100)
        self.right_motor.set_speed(-100)
        time.sleep(1.2)  # Time to rotate 90 degrees; adjust as needed
        self.stop_robot()

    def rotate_right(self):
        self.display_message("rotating right")
        self.left_motor.set_speed(100)
        self.right_motor.set_speed(100)
        time.sleep(1.2)  # Time to rotate 90 degrees; adjust as needed
        self.stop_robot()

    def stop_robot(self):
        self.display_message("stopped")
        self.left_motor.stop()
        self.right_motor.stop()

    def handle_input(self):
        """
        Handle user input to control the robot.
        W -> Move forward
        S -> Move backward
        A -> Rotate left
        D -> Rotate right
        Q -> Stop the robot
        """
        while True:
            command = input("Enter command (W: forward, S: backward, A: left, D: right, Q: stop & quit): ").strip().lower()

            if command == "w":
                self.move_forward()
            elif command == "s":
                self.move_backward()
            elif command == "a":
                self.rotate_left()
            elif command == "d":

                self.rotate_right()
            elif command == "q":
                self.stop_robot()
                break
            else:
                print("Invalid command. Please enter W, S, A, D, or Q.")

            time.sleep(0.1)  # Small delay for processing

def main():
    pi = pigpio.pi()
    robot = RobotControl(pi)

    try:
        print("Control the robot by entering commands: W (forward), S (backward), A (left), D (right), Q (stop and exit)")
        robot.handle_input()
    finally:
        pi.stop()
        print("Robot control terminated.")

if __name__ == "__main__":
    main()