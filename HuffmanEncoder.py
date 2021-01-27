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


def split_image(image_rgb):
	return cv2.split(image_rgb)


def ravel_image(image_gray):
	return image_gray.ravel()

def adaptive_encode(image_shape):
	result = list()
	for ele in image_shape:
		ele_1 = ele // 255
		ele_2 = ele % 255
		result.extend([ele_1,ele_2])
	return result


def write_shape(shape):
	shape_encoded = adaptive_encode(shape)
	
	file_shape = open("shape.bin","wb")
	file_shape.write(bytearray(shape_encoded))
	file_shape.close()
	
	#print("shape_written")
	return shape_encoded


class HeapNode:
	def __init__(self,val,freq):
		self.val = val
		self.freq = freq
		self.left = None
		self.right = None
	
	def __lt__(self,other):
		if other == None:
			return -1
		if not isinstance(other,HeapNode):
			return -1
		return self.freq < other.freq
	
	def __str__(self):
		if isinstance(self.val,numpy.uint8):
			return "%d:%d" % (self.val,self.freq)
		else:
			return "None:%d" % (self.freq)


class Huffman:
	def __init__(self,data,channel):
		self.data = data
		self.heap = list()
		self.codes = dict()
		self.reverse_mapping = dict()
		self.channel = channel
	
	def make_frequency_dict(self,data):
		frequency = dict()
		for val in data:
			frequency[val] = frequency.get(val,0) + 1
		return frequency
	
	def make_heap(self,frequency):
		for key in frequency:
			node = HeapNode(key,frequency[key])
			heapq.heappush(self.heap,node)
	
	def merge_nodes(self):
		while len(self.heap) > 1:
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)
			
			merged = HeapNode(None,node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2
			
			heapq.heappush(self.heap,merged)
	
	def make_codes_helper(self,root,current_code):
		if root == None:
			return None
		if root.val != None:
			self.codes[root.val] = current_code
			self.reverse_mapping[current_code] = root.val
			return
		self.make_codes_helper(root.left,current_code + "0")
		self.make_codes_helper(root.right,current_code + "1")
	
	def make_codes(self):
		root = heapq.heappop(self.heap)
		current_code = ""
		self.make_codes_helper(root,current_code)
	
	def get_encoded_data(self,data):
		encoded_data = ""
		for val in data:
			encoded_data += self.codes[val]
		return encoded_data
	
	def pad_encoded_data(self,encoded_data):
		extra_padding = 8 - len(encoded_data) % 8
		for i in range(extra_padding):
			encoded_data += "0"
		
		padded_info = "{0:08b}".format(extra_padding)
		encoded_data = padded_info + encoded_data
		return encoded_data
	
	def get_byte_array(self,padded_encoded_data):
		if len(padded_encoded_data) % 8 != 0:
			#print("encoded data not padded properly")
			exit(0)
		
		b = bytearray()
		for i in range(0,len(padded_encoded_data),8):
			byte = padded_encoded_data[i:i + 8]
			b.append(int(byte,2))
		return b
	
	def compress(self):
		file_channel = "compress" + str(self.channel) +".bin"
		output = open(file_channel,"wb")
		
		frequency = self.make_frequency_dict(self.data)
		self.make_heap(frequency)
		self.merge_nodes()
		self.make_codes()
		
		encoded_data = self.get_encoded_data(self.data)
		padded_encoded_data = self.pad_encoded_data(encoded_data)
		
		b = self.get_byte_array(padded_encoded_data)
		output.write(b)
		
		#print("channel: %d" % (self.channel),"compressed")
		output.close()
		return "compress" + str(self.channel) + ".bin"
	
	""" write reverse_mapping """
	
	def write_reverse_mapping(self):
		file_keys = open("keys" + str(self.channel) + ".bin","wb")
		file_vals = open("vals" + str(self.channel) + ".bin","wb")
		file_carry = open("carry" + str(self.channel) + ".bin","wb")
		
		keys = list(self.reverse_mapping.keys())
		vals = list(self.reverse_mapping.values())
		carry = [len(str(ele)) for ele in keys]
		
		encoded_keys = ""
		for ele in keys:
			encoded_keys += ele
		
		padded_encoded_keys = self.pad_encoded_data(encoded_keys)
		b_keys = self.get_byte_array(padded_encoded_keys)
		file_keys.write(b_keys)
		
		
		file_vals.write(bytearray(vals))
		file_carry.write(bytearray(carry))
		
		file_keys.close()
		file_vals.close()
		file_carry.close()
		
		#print("channel: %d" % (self.channel),"reverse_mapping written")


def run():
	image_rgb = get_image_rgb("colors.jpg")
	r,g,b = split_image(image_rgb)
	channels = [r,g,b]
	for i in range(3):	
		data = ravel_image(channels[i])
	
		huffman = Huffman(data,i)
		encoded_file_name = huffman.compress()
		
		""" write reverse_mapping """
		
		huffman.write_reverse_mapping()
	
	""" write shape """
	
	shape = r.shape
	
	write_shape(shape)

if __name__ == "__main__":
	start = time.time()
	run()
	end = time.time() - start
	print(end, ' s')
	
	














