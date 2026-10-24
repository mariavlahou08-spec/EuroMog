import serial
import time
import json
import random

# Initialize your serial connection (adjust 'COM3' or '/dev/ttyUSB0' and baudrate as needed)
ser = serial.Serial('/dev/cu.usbmodem14101', 115200, timeout=1)

def measure(ser=None, use_simulator=False):
    """
    Reads the latest vibration data from the ESP32 via USB serial.
    Includes a simulator toggle for the software fallback[cite: 4].
    """
    if use_simulator:
        # Mock data for the simulator
        return {
            "1x_peak": round(random.uniform(0.1, 0.8), 3),
            "rms_vibration": round(random.uniform(0.2, 1.2), 3),
            "health_score": random.choice(["green", "yellow", "red"])
        }
    
    if ser and ser.in_waiting > 0:
        # Read the latest line from the USB serial buffer
        line = ser.readline().decode('utf-8').strip()
        try:
            # Assuming the ESP32 sends data like: {"1x_peak": 0.45, "rms_vibration": 0.6}
            data = json.loads(line)
            return data
        except json.JSONDecodeError:
            return {"error": f"Failed to parse JSON from ESP32: {line}"}
            
    return {"error": "No data available on serial buffer"}


def speed_sweep(start_speed, end_speed, step, ser=None, use_simulator=False):
    """
    Steps through a range of speeds to find the resonance peak[cite: 4].
    Calls the existing set_speed control function and the new measure function.
    """
    sweep_results = []
    
    for current_speed in range(start_speed, end_speed + 1, step):
        # 1. Command the motor (replace 'set_speed' with your actual existing function name)
        set_speed(current_speed) 
        
        # 2. Allow the physical motor and PID loop time to stabilize at the new RPM
        time.sleep(0.5) 
        
        # 3. Read the resulting vibration
        vibration_data = measure(ser=ser, use_simulator=use_simulator)
        
        # 4. Log the data point
        sweep_results.append({
            "speed": current_speed,
            "vibration": vibration_data
        })
        
    return sweep_results