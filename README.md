# ESP32 Captive Portal

Author: Cabzla

This project provides a minimal captive portal implementation for the ESP32 microcontroller, allowing users to create a WiFi hotspot with a landing page where users can log in to access the network.

## Overview

The ESP32 Captive Portal project enables ESP32 devices to act as access points (APs) broadcasting a WiFi network. When users connect to this network and attempt to access any website, they are redirected to a landing page hosted on the ESP32. This landing page typically presents a login form or some information about the network.

## Features

- Simple setup of an access point with customizable SSID and landing page.
- HTTP server for handling client requests and serving HTML content.
- DNS server to redirect all DNS queries to the ESP32 landing page.
- Handles image and video display on requests.
- Provides a basic example of a captive portal for WiFi authentication.

## Getting Started

To use the ESP32 Captive Portal, follow these steps:

1. Set up the ESP32 device with the required hardware and software.
2. Configure the access point settings in the code, such as SSID and IP address.
3. Upload the code to the ESP32 device.
4. Connect to the WiFi network broadcasted by the ESP32.
5. Open a web browser and attempt to access any website.
6. You will be redirected to the captive portal landing page hosted on the ESP32.
7. Follow the instructions on the landing page to log in or access the network.

## Dependencies

- MicroPython: The project is written in MicroPython, a lean and efficient implementation of the Python 3 programming language, optimized to run on microcontrollers.
- uasyncio: The asyncio-based asynchronous I/O framework for MicroPython, used for handling HTTP and DNS requests asynchronously.
- ESP32 Microcontroller: The project is designed to run on ESP32 microcontrollers, which offer built-in WiFi capabilities.

## Usage

The project provides a flexible foundation for implementing custom captive portal solutions on ESP32 devices. Users can customize the landing page HTML, CSS, and JavaScript to suit their specific requirements for WiFi authentication and network access.

## Contributions

Contributions to the ESP32 Captive Portal project are welcome! If you encounter any issues, have feature requests, or would like to contribute improvements, please feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the [MIT License](LICENSE).
