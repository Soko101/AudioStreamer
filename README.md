# AudioStreamer
Simple audio streaming application using TCP/UDP in python

The client and server code for the audio streaming application utilizes a network programming approach 
with sockets to transmit audio data between a client and a server:

Architecture Overview

This audio streaming application is designed around a client-server architecture that enables 
real-time audio streaming over the network. The application supports both UDP and TCP protocols for 
data transmission, providing flexibility in balancing between lower latency (UDP) and reliable data transmission (TCP).

Server

Module Dependencies: Uses the socket, argparse, signal, pyaudio, and sys modules.

Functionality:

The server initializes a socket connection on a specified port and listens for incoming audio streams from the client.
It uses the pyaudio library to play the incoming audio stream in real-time.
A signal handler is implemented to gracefully shut down the server on receiving 
a SIGINT signal, ensuring that resources are properly released.

Client

Module Dependencies: Similar to the server, it utilizes the socket, argparse, signal, pyaudio, sys, 
and additionally, the queue module for buffering audio data.

Functionality:

The client captures audio input from a microphone using the pyaudio library.
Audio data is then sent to the server over a socket connection, either using UDP or TCP, based on the user's choice.
Implements a signal handler to intercept SIGINT signals for a graceful shutdown, closing the socket and releasing resources properly.

Key Features

Flexibility in Protocol Choice: The application can be configured to use either UDP or TCP for audio 
data transmission, offering a trade-off between speed and reliability.
Real-Time Audio Streaming: Leverages the pyaudio library for capturing and playing audio in 
real-time, facilitating live audio streaming over the network.
Graceful Shutdown: Both the client and server are equipped with signal handlers to manage
unexpected exits, ensuring that resources are not left hanging.

Usage

Both the client and server scripts accept command-line arguments to specify the protocol (--protocol with options udp or tcp).
The server must be started before the client and set to listen on a specific port.
The client then connects to the server's IP address and port, beginning the audio stream.
