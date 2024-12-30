# IoT-Based Smart Parking System 🚗

This project is an **IoT-based Smart Parking Management System** designed to optimize parking space utilization and enhance security at Strathmore University. It uses **Raspberry Pi**, **ultrasonic sensors**, and **RFID technology** to monitor parking slots in real-time and provide a user-friendly web interface for parking management.

## Key Features ✨
- **Real-Time Parking Slot Monitoring**: Ultrasonic sensors detect parking space occupancy.
- **RFID Authentication**: Only authorized vehicles can access designated parking areas.
- **Web Interface**: Users can view available slots and book parking spaces.
- **Role-Based Access**: Different roles (Student, Staff, Visitor, Parking Security) for controlled access.
- **Security Alerts**: Emergency alerts and location tracking for enhanced safety.

## Hardware Components 🛠️
- Raspberry Pi 4
- Ultrasonic Sensors (HC-SR04)
- RFID Readers and Tags
- IR Sensors
- LED Indicators
- Breadboard and Jumper Wires
- Power Supply (5V adapter)
- Camera Module (optional)
- Display Screen (optional)

## Software Tools 💻
- **Python**: For system logic and hardware control.
- **Flask**: Web framework for the user interface.
- **Firebase**: Real-time data storage and analysis.
- **HTML/CSS/JavaScript**: Front-end development.

## How It Works 🚀
1. **Parking Detection**: Ultrasonic sensors detect if a parking slot is occupied.
2. **User Authentication**: RFID tags verify vehicle access.
3. **Real-Time Updates**: Parking slot status is updated on the web interface.
4. **Booking**: Users can book available slots via the web app.
5. **Security**: Emergency alerts and location tracking ensure safety.

## Setup Instructions 📋
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up Firebase and configure `serviceAccountKey.json`.
4. Connect hardware components to the Raspberry Pi.
5. Run the Flask app: `python app.py`.

## Future Enhancements 🔮
- Integration with mapping APIs for navigation.
- Advanced analytics for parking usage patterns.
- Mobile app for easier access.

## License 📜
This project is open-source and available under the MIT License.

