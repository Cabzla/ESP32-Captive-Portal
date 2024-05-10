"""
Author: Cabzla

This script creates a minimal captive portal for a WiFi hotspot, allowing users to connect to an ESP32 device and access a landing page where they can login to the WiFi network.

It provides functionality to handle HTTP requests, serve HTML content, and respond to DNS queries.

"""

import gc  # Import the garbage collector module
import sys  # Import the sys module for system-specific parameters and functions
import network  # Import the network module for network interfaces
import socket  # Import the socket module for low-level networking
import uasyncio as asyncio  # Import the uasyncio module for asynchronous I/O

# Helper to detect uasyncio v3
IS_UASYNCIO_V3 = hasattr(asyncio, "__version__") and asyncio.__version__ >= (3,)


# Access point settings
SERVER_SSID = 'Free Highspeed Wifi'  # Set the SSID for the access point
SERVER_IP = '10.0.0.1'  # Set the IP address for the access point
SERVER_SUBNET = '255.255.255.0'  # Set the subnet mask for the access point


def wifi_start_access_point():
    """Set up the access point."""
    wifi = network.WLAN(network.AP_IF)  # Create a WLAN object for the access point
    wifi.active(True)  # Activate the access point
    wifi.ifconfig((SERVER_IP, SERVER_SUBNET, SERVER_IP, SERVER_IP))  # Configure the access point's network interface
    wifi.config(essid=SERVER_SSID, authmode=network.AUTH_OPEN)  # Configure the access point's SSID and authentication mode
    print('Network config:', wifi.ifconfig())  # Print the network configuration


def _handle_exception(loop, context):
    """Handle exceptions globally (uasyncio v3 only)."""
    print('Global exception handler')  # Print a message indicating the global exception handler is invoked
    sys.print_exception(context["exception"])  # Print the exception details
    sys.exit()  # Exit the system


class DNSQuery:
    """Class to handle DNS queries."""

    def __init__(self, data):
        self.data = data
        self.domain = ''
        tipo = (data[2] >> 3) & 15  # Opcode bits
        if tipo == 0:  # Standard query
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
                ini += lon + 1
                lon = data[ini]
        print("DNSQuery domain:" + self.domain)

    def response(self, ip):
        """Generate DNS response."""
        print("DNSQuery response: {} ==> {}".format(self.domain, ip))
        if self.domain:
            packet = self.data[:2] + b'\x81\x80'
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
            packet += self.data[12:]  # Original Domain Name Question
            packet += b'\xC0\x0C'  # Pointer to domain name
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, ip.split('.')))  # 4bytes of IP
        return packet


class MyApp:
    """Main application class."""

    async def start(self):
        """Start the application."""
        # Get the event loop
        loop = asyncio.get_event_loop()

        # Add global exception handler
        if IS_UASYNCIO_V3:
            loop.set_exception_handler(_handle_exception)

        # Start the wifi AP
        wifi_start_access_point()

        # Create the server and add task to event loop
        server = asyncio.start_server(self.handle_http_connection, "0.0.0.0", 80)
        loop.create_task(server)

        # Start the DNS server task
        loop.create_task(self.run_dns_server())

        # Start looping forever
        print('Looping forever...')
        loop.run_forever()

    async def handle_http_connection(self, reader, writer):
        """Handle HTTP connections."""
        gc.collect()

        # Get HTTP request line
        data = await reader.readline()
        request_line = data.decode()
        addr = writer.get_extra_info('peername')
        print('Received {} from {}'.format(request_line.strip(), addr))

        # Read headers, to make client happy (else curl prints an error)
        while True:
            gc.collect()
            line = await reader.readline()
            if line == b'\r\n':
                break

        # Handle the request
        if len(request_line) > 0:
            if request_line.startswith("GET /image.jpg"):
                # Respond with the image file
                try:
                    with open('image.jpg', 'rb') as f:
                        await writer.awrite('HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\n\r\n')
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            await writer.awrite(chunk)
                except OSError:
                    # Image file not found
                    await writer.awrite('HTTP/1.0 404 Not Found\r\n\r\n')
            elif request_line.startswith("GET /video.mp4"):
                # Respond with the video file
                try:
                    with open('video.mp4', 'rb') as f:
                        await writer.awrite('HTTP/1.0 200 OK\r\nContent-Type: video/mp4\r\n\r\n')
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            await writer.awrite(chunk)
                except OSError:
                    # Video file not found
                    await writer.awrite('HTTP/1.0 404 Not Found\r\n\r\n')
            else:
                # Respond with the HTML content
                response = 'HTTP/1.0 200 OK\r\n\r\n'
                with open('index.html') as f:
                    response += f.read()
                await writer.awrite(response)

        # Close the socket
        await writer.aclose()

    async def run_dns_server(self):
        """Handle incoming DNS requests."""
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        udps.bind(('0.0.0.0', 53))

        while True:
            try:
                # gc.collect()
                if IS_UASYNCIO_V3:
                    yield asyncio.core._io_queue.queue_read(udps)
                else:
                    yield asyncio.IORead(udps)
                data, addr = udps.recvfrom(4096)
                print("Incoming DNS request...")

                DNS = DNSQuery(data)
                udps.sendto(DNS.response(SERVER_IP), addr)

                print("Replying: {:s} -> {:s}".format(DNS.domain, SERVER_IP))

            except Exception as e:
                print("DNS server error:", e)
                await asyncio.sleep_ms(3000)

        udps.close()


# Main code entrypoint
try:
    # Instantiate app and run
    myapp = MyApp()

    if IS_UASYNCIO_V3:
        asyncio.run(myapp.start())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myapp.start())

except KeyboardInterrupt:
    print('Bye')

finally:
    if IS_UASYNCIO_V3:
        asyncio.new_event_loop()  # Clear retained state
