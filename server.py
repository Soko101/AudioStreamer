import socket
import argparse
import signal
import pyaudio
import sys

# signal handler
def handler(signum, frame):
    global playStream, server_socket
    print("Exiting the program")
    playStream.stop_stream()
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

# command line arguments
parser=argparse.ArgumentParser(description="AudioStream client")
parser.add_argument("--protocol", required=False, default='udp', choices=['udp', 'tcp'])
parser.add_argument("--port", required=False, default=12345)
parser.add_argument("--size", required=False, default=10, type=int, choices=range(10, 151, 10))
args=parser.parse_args()

print("Protocol:", args.protocol.upper())
print("Port:", args.port)
print("Size:", args.size, "ms")

# audio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 441 # 10 ms
NUMCHUNKS = int(args.size / 10)

pyaudioObj = pyaudio.PyAudio()

playStream = pyaudioObj.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True,
                            frames_per_buffer=CHUNK * NUMCHUNKS)
silence = 0
silenceData = silence.to_bytes(2) * CHUNK * NUMCHUNKS

print("PyAudio Device Initialized")

# socket
if args.protocol == 'udp':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', args.port))
else:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', args.port))
    server_socket.listen()
    connection, source = server_socket.accept()

print("Socket Initialized")

def recvData():
    global expectedSeqNum, playStream, silenceData, server_socket, connection

    print("Expecting Sequence #", expectedSeqNum)

    if args.protocol == 'udp':
        data, address = server_socket.recvfrom(CHUNK * NUMCHUNKS * 2 + 2)
    else:
        data = connection.recv(CHUNK * NUMCHUNKS * 2 + 2)
        while len(data) < CHUNK * NUMCHUNKS * 2 + 2:
            data += connection.recv(CHUNK * NUMCHUNKS * 2 + 2 - len(data))

    sequenceNumber = int.from_bytes(data[:2], byteorder="little", signed=False)
    audioData = data[2:]

    if expectedSeqNum == sequenceNumber:
        # play
        print("Received Sequence #", sequenceNumber, "(", len(data), "bytes)")
        playStream.write(audioData)

        expectedSeqNum = (expectedSeqNum + 1) % 65536
    else:
        print("Received Out of Sequence #", sequenceNumber, "(", len(data), "bytes)")
        # play silence
        playStream.write(silenceData)

        if sequenceNumber > expectedSeqNum:
            # catch up
            expectedSeqNum = sequenceNumber + 1


expectedSeqNum = 0

while True:
    recvData()

