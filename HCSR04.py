import RPi.GPIO as gpio
import time

class HCSR04:
    # Encapsulates the attributes and methods to use the HC-SR04 ultra-sound distance sensor
    trig = 0
    echo = 0
    const_cm = 17014.50
    const_in = 6698.62
    const_ft = 558.2

    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo

        gpio.setmode(gpio.BOARD)
        gpio.setup(self.trig, gpio.OUT)
        gpio.setup(self.echo, gpio.IN)
        gpio.output(self.trig, False)
        time.sleep(0.3)  # Allow sensor to settle

    def delete(self):
        gpio.cleanup()
        print("All clean")

    def measure(self, samples, unit):
        valid_samples = 0
        acc = 0.0
        # Set a timeout (in seconds) for waiting loops. Adjust if necessary.
        timeout = 0.02

        for _ in range(samples):
            # Send trigger pulse
            gpio.output(self.trig, True)
            time.sleep(0.00001)
            gpio.output(self.trig, False)

            # Wait for echo to go high
            start_time = time.time()
            while gpio.input(self.echo) == 0:
                if time.time() - start_time > timeout:
                    break
            pulse_start = time.time()

            # Wait for echo to go low
            while gpio.input(self.echo) == 1:
                if time.time() - pulse_start > timeout:
                    break
            pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            # If pulse_duration is too short, skip this sample
            if pulse_duration <= 0.00001:
                continue

            # Calculate distance based on the chosen unit
            if unit == "cm":
                distance = pulse_duration * self.const_cm
            elif unit == "in":
                distance = pulse_duration * self.const_in
            elif unit == "ft":
                distance = pulse_duration * self.const_ft
            else:
                raise ValueError("Invalid unit. Use 'cm', 'in', or 'ft'.")

            acc += distance
            valid_samples += 1

        if valid_samples == 0:
            return 0.0

        return round(acc / valid_samples, 2)
