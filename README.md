# Alteryx SDK MQTT Client
MQTT Client for Alteryx using the Python SDK

Custom Alteryx SDK tool used to connect to an MQTT broker and subscribe to topics for a given time period. Advertising packets sent to the broker will be received by the client and pushed out of the tool.

## Installation
Download the yxi file and double click to install in Alteyrx. 

<img src="https://github.com/bobpeers/Alteryx_SDK_MQTT_Client/blob/main/images/MQTT_Install.png" width="600" alt="MQTT Client Install Dialog">

The tool will be installed in the __Connector__ category.

<img src="https://github.com/bobpeers/Alteryx_SDK_MQTT_Client/blob/main/images/mqtt_tool.png" width="600" alt="Alteryx Connector Category">

## Requirements

This tool will install the [Paho MQTT library](https://pypi.org/project/paho-mqtt/)

## Usage
This tool takes no inputs and receives messages for a user selected time period before pushing the topic and messages downstream.

## Outputs
The output includes topic and raw message data.


## Usage
This workflow demonstrates the tool in use and the output data. The workflow shown here:

<img src="https://github.com/bobpeers/Alteryx_SDK_MQTT_Client/blob/main/images/mqtt_workflow.png" width="1000" alt="MQTT Workflow">
