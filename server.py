# Basic websockets implementation. Definitely does not meet the standard.
import socket
from base64 import b64encode
from hashlib import sha1

# Create a TCP server socket on port 8887
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = (socket.gethostbyname(socket.gethostname()), 8887) # Bind the socket to the computer's IP
sock.bind(host)
sock.listen(5)
 
print("TCP socket listening on " + str(host))

# All this bullshit might only be necessary for the first byte of the message.

def bitlen(n):	# Return the length in bits of a number (number of digits when represented in binary)
	l = 0
	while n:
		n >>= 1
		l += 1
	return l

def to_bits(str): 	# Takes a string and turns it into a string of bits, like '00001101'. Inefficient, as it effectively multiplies the length by 8.
	data = ""		# Every character will be represented as 8 bits, including leading zeros. So '\x01' -> '00000001'
	for c in str:
		c = ord(c)
		b = bin(c)[2:] # remove the '0b'
		data += '0'*(8-bitlen(c))+b # Add the leading zeros
	return data

def chars_to_int(data): # takes an array of chars and returns an integer representing them
	n = 0
	for e in data:
		n << 8
		n += ord(e)
	return n

def unmask(msg, key): # where msg is a string.
	#len = msg[9:9+7+64+1] 
	#key = msg[16+128:48+128] # These are bit indices. I think we need bytes instead.
	# Server messages are not masked
	# Client messages are masked according to sec 5.3 of RFC 6455
	# All of this has to be done with a bit array
	print "not yet implemented"
	throw(Exception)
	
def parse(msg):
	data = []
	for e in msg:
		data.append(e) # Convert the message string to an array (makes things slightly neater)
		
	first_byte = to_bits(data.pop(0)) # Contains FIN bit, RSV bits, and opcode
	mask = 1 if data[0] > 127 else 0 # see if the first bit is 1. It should be.
	paylen_bits = to_bits(data[0])
	payload_len = ord(data.pop(0))
	payload_len = payload_len if payload_len < 126 else payload_len - 128 # -128 removes the first bit
	payload_len_ext = ['\x00']	
	if payload_len == 126 or payload_len == 127:
		payload_len_ext = data[0:2] # 7+16 bit payload length
		del data[0:2]
		if payload_len == 127:
			payload_len_ext = data[0:6] # 7+64 bit payload length
			del data[0:6]
	masking_key = data[0:4]
	del data[0:4] # All that's left now is payload data
	
	print "First byte: " + str(first_byte)
	print "Masking bit: " + str(mask)
	print "Payload length: " + paylen_bits
	print "Payload length (int): " + str(payload_len)
	print "Extended payload length (int): " + str(chars_to_int(payload_len_ext))
	print "Masking key: " + str(masking_key)
	print "Actual payload length: " + str(len(data))
	
data = ''
header = ''

client, address = sock.accept()

while True:
	header += str(client.recv(16)) # It's already a str in python 2.7. This is for compatibility.
	if header.find('\r\n\r\n') != -1:
		key = header.find("Sec-WebSocket-Key: ")
		print(key)
		key = header[key+19:key+24+19] # Probably shouldn't hardcode this. 19 is length of the searched str, 24 is length of key
		print(key)
		key = b64encode(sha1(key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
		header = header.split('\r\n')
		for e in header:
			print(e)
		print("end of header")
		data = header.pop()
		#origin = header[-2][9:] # Do I actually need this?
		handshaken = True
		handshake = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n" % key
		client.send(handshake)
		break

print("All handshaken!")
while True:
	tmp = str(client.recv(8192)) # We want to handle this as a string of bits, but python 2.7 will only give a regular string
	parse(tmp)
	
