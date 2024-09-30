from flask import Flask
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def calculate():
    app.logger.info("Received request, starting calculation")
    # More CPU-intensive calculation
    result = 0
    for i in range(1000000):  # Reduced range
        result += i * i  # Simpler calculation
    time.sleep(0.1)  # Simulate some I/O operation
    app.logger.info(f"Calculation completed, result: {result}")
    return f"Calculation result: {result}"

if __name__ == '__main__':
    app.logger.info("Starting the application")
    app.run(host='0.0.0.0', port=5000)