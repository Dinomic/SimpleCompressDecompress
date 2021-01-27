import cv2
import numpy
import matplotlib.pyplot as plt
import heapq
import time
def get_image_rgb(image_name):
	image = cv2.imread(image_name)
	image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
	return image


def show_image_rgb(image_rgb):
	plt.imshow(image_rgb)
	plt.show()


def merge_channels(channels):
	return cv2.merge((channels))


def ravel_image(image_gray):
	return image_gray.ravel()


def adaptive_decode(shape_encoded):
	return [shape_encoded[0] * 255 + shape_encoded[1],shape_encoded[2] * 255 + shape_encoded[3]]


class Huffman:
	def __init__(self,channel):
		self.channel = channel
		file_keys = open("keys" + str(self.channel) + ".bin","rb")
		file_vals = open("vals" + str(self.channel) + ".bin","rb")
		file_carry = open("carry" + str(self.channel) + ".bin","rb")
		
		bit_string = ""
		byte = file_keys.read(1)
		while len(byte) != 0:
			byte = ord(byte)
			bits = bin(byte)[2:].rjust(8,"0")
			bit_string += bits
			byte = file_keys.read(1)
		
		keys_string = self.remove_padding(bit_string)
		
		carry = list(file_carry.read())
		vals = list(file_vals.read())
		keys = list()
		
		for ele in carry:
			keys.append(keys_string[:ele])
			keys_string = keys_string[ele:]
		
		self.reverse_mapping = dict()
		for i in range(len(keys)):
			self.reverse_mapping[keys[i]] = vals[i]
		
		file_keys.close()
		file_vals.close()
		file_carry.close()
		
		#print("channel: %d" % (self.channel),"reverse_mapping built")
	
	""" decompression """
	
	def remove_padding(self,padded_encoded_data):
		padded_info = padded_encoded_data[:8]
		extra_padding = int(padded_info,2)
		
		padded_encoded_data = padded_encoded_data[8:]
		encoded_data = padded_encoded_data[:-1 * extra_padding]
		return encoded_data
	
	def decode_data(self,encoded_data):
		current_code = ""
		decoded_data = numpy.empty(0,dtype = "uint8")
		
		for bit in encoded_data:
			current_code += bit
			if current_code in self.reverse_mapping:
				val = self.reverse_mapping[current_code]
				decoded_data = numpy.append(decoded_data,val)
				current_code = ""
		return decoded_data
	
	def decompress(self,encoded_file_name):
		file_in = open(encoded_file_name,"rb")
		bit_string = ""
		byte = file_in.read(1)
		while len(byte) != 0:
			byte = ord(byte)
			bits = bin(byte)[2:].rjust(8,"0")
			bit_string += bits
			byte = file_in.read(1)
		
		encoded_data = self.remove_padding(bit_string)
		#print("remove_padding done")
		decompressed_data = self.decode_data(encoded_data)
		
		#file_in.close()
		#print("decompressed")
		return decompressed_data


def run():
	start = time.time()
	file_shape = open("shape.bin","rb")
	shape_encoded = list(file_shape.read())
	shape = adaptive_decode(shape_encoded)
	
	channels = list()
	
	for i in range(3):
		huffman = Huffman(i)
	
		encoded_file_name = "compress" + str(huffman.channel) +".bin"
		decompressed_data = huffman.decompress(encoded_file_name)
		
		channel = numpy.reshape(decompressed_data,shape).astype("uint8")
		channels.append(channel)
	
	pic = merge_channels(channels)
	
	end = time.time() - start
	print(end, ' s')
	show_image_rgb(pic)
	
	file_shape.close()


if __name__ == "__main__":
	
	run()
	






















