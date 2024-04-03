import socket
import argparse
import signal
import pyaudio
import sys
import queue

# signal handler
def handler(signum, frame):
    global recordStream, client_socket
    print("Exiting the program")
    recordStream.stop_stream()
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

# command line arguments
parser=argparse.ArgumentParser(description="AudioStream client")
parser.add_argument("--protocol", required=False, default='udp', choices=['udp', 'tcp'])
parser.add_argument("--host", required=False, default="localhost")
parser.add_argument("--port", required=False, default=12345)
parser.add_argument("--size", required=False, default=10, type=int, choices=range(10, 151, 10))
args=parser.parse_args()

print("Protocol:", args.protocol.upper())
print("Host:", args.host)
print("Port:", args.port)
print("Size:", args.size, "ms")

# audio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 441 # 10 ms
NUMCHUNKS = int(args.size / 10)

# let's use a callback to read instead
sendQueue = queue.Queue() # store the audio data to send

# create a bogus silence data for the callback function
silence = 0
silenceData = silence.to_bytes(2) * CHUNK * NUMCHUNKS

sequenceNumber = 0

# define the callback function (called everytime there is input data)
def record(data, frame_count, time_info,  status):
    global sendQueue

    sendQueue.put(data)

    return (silenceData, pyaudio.paContinue)

pyaudioObj = pyaudio.PyAudio()

recordStream = pyaudioObj.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=NUMCHUNKS * CHUNK,
                                stream_callback=record)

print("PyAudio Device Initialized")

# socket
if args.protocol == 'udp':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
else:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.host, args.port))

def sendAudio():
    global client_socket, destination, sequenceNumber, sendQueue

    audioData = sendQueue.get()

    seqBytes = sequenceNumber.to_bytes(2, byteorder="little", signed=False)

    sendData = seqBytes + audioData

    print("Sending Sequence #", sequenceNumber, "(", len(sendData), "bytes)")

    if args.protocol == 'udp':
        client_socket.sendto(sendData, destination)
    else:
        client_socket.sendall(sendData)

    sequenceNumber += 1

destination = (args.host, args.port)

# start streaming

while True:
    sendAudio()

