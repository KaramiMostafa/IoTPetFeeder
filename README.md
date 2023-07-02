# **Remote Pet Feeding and Monitoring System**
This project provides an end-to-end IoT analytics solution that includes device simulation, service catalog, and a connector to ThingSpeak for data visualization. The project utilizes Python programming language, MQTT protocol for device communication, and CherryPy for providing web services.

The project consists of five Python scripts. To run the project correctly, you need to follow the steps mentioned below in order. Each of these Python scripts plays a different role:

- **Catalog.py**: Maintains a catalog of devices and services, their attributes, and the topics on which they publish/subscribe.

- **sensor.py**: Simulates a weight sensor. The sensor values are published to a specific topic on the MQTT broker.

- **servo.py**: This is a web service that publishes a turn-on message to a specific topic on the MQTT broker when it receives a POST request.

- **tsConnector.py**: Connects with the ThingSpeak IoT analytics service. It listens for incoming sensor messages, parses them, and then publishes the data to ThingSpeak for further analysis.

- Bot3.py: This script was not provided, but based on the naming and context, it likely represents an additional IoT device or a controller script.

## **How to Run**
Please follow the steps below to run the project:

Run Catalog.py: Start the service catalog first as it maintains the records of devices and services. To do so, use the command python Catalog.py in your command line. Ensure that you are in the correct directory where the Catalog.py file is located.

Run sensor.py: Now, start the sensor script with the command python sensor.py. This script will simulate sensor readings and publish them to an MQTT broker.

Run servo.py: Start the servo service using python servo.py. It will listen for HTTP POST requests and publish a corresponding message on an MQTT topic.

Run tsConnector.py: Start the ThingSpeak Connector using python tsConnector.py. It will subscribe to the sensor readings from the MQTT broker and forward them to the ThingSpeak service for data visualization and analysis.

Run Bot3.py: Start the Bot3 script (if available) by running python Bot3.py. The exact functionality of this script was not provided but, it should be started last based on the context provided.

Ensure that all these scripts are running simultaneously, ideally in separate terminal windows. This will ensure the proper functioning of this project.

Please note that for the above commands to work, you must have Python installed on your machine. Replace python with python3 if you're on a machine where Python version 3.x is not the default. Also, make sure all the dependencies specified in the project are installed (use pip or conda to install them).

**IMPORTANT**: This project relies on various *JSON*** files for its configuration. These files contain essential data like device IDs, broker addresses, etc., which should match the actual IoT environment where this project is deployed.