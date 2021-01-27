import cv2
import numpy as np
import heapq
from array import *
import time

class HeapNode:
	def __init__(self,val,freq):
		self.val = val
		self.freq = freq
		self.left = None
		self.right = None
	
	def __lt__(self,other):
		if other == None:
			return -1
		if not isinstance(other, HeapNode):
			return -1
		return self.freq < other.freq
	
	def __str__(self):
		if isinstance(self.val,np.uint8):
			return "%d:%d" % (self.val,self.freq)
		else:
			return "None:%d" % (self.freq)

def make_data (r, g, b):
	rr = r.ravel()
	gg = g.ravel()
	bb = b.ravel()

	yinyang = ''
	result = list()
	sub = list()

	result.extend(rr)
	sub.extend(rr)
	result.extend(gg)
	sub.extend(gg)
	result.extend(bb)
	sub.extend(bb)
	
	for i in range(1,len(result)):
		a = int(sub[i]) - int(sub[i-1])
		if a < 0:
			yinyang += '0'
			result[i] = -a
		else:
			yinyang += '1'
			result[i] = a
	
	#print(len(result))
	#print(len(yinyang))
	return result, yinyang

def make_freq_dict(data):
	freq_d = {}
	for ele in data:
		if not ele in freq_d:            
			freq_d[ele] = 0
		freq_d[ele] += 1
	return freq_d

def make_heap(freq_d):
    heap = list()
    for key in freq_d:
        node = HeapNode(key, freq_d[key])
        heapq.heappush(heap,node)
    return heap

def merge_node(heap):
    while (len(heap) > 1):
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)

        node3 = HeapNode(None, node1.freq + node2.freq)
        node3.left = node1
        node3.right = node2

        heapq.heappush(heap, node3)

def sub_make_code(root,current_code, code_dict, recode_dict):
    if (root == None):
        return
    if (root.val != None):
        code_dict[root.val] = current_code
        recode_dict[current_code] = root.val
        return
    sub_make_code(root.left, current_code + '0', code_dict, recode_dict)
    sub_make_code(root.right, current_code + '1', code_dict, recode_dict)

def make_code(heap):
    code_dict = {}
    recode_dict = {}
    root = heapq.heappop(heap)
    current_code = ''
    sub_make_code(root, current_code, code_dict, recode_dict)
    return code_dict, recode_dict
	
def get_encoded_data(data, code_dict):
	encoded_data = ''
	i = 0
	for val in data:	
		encoded_data += code_dict[val]
	return encoded_data

def pad_encoded_data(encoded_data):
	extra_padding = 8 - len(encoded_data) % 8
	for i in range(extra_padding):
		encoded_data += "0"
	padded_info = "{0:08b}".format(extra_padding)
	encoded_data = padded_info + encoded_data
	return encoded_data

def get_byte_array(padded_encoded_data):
	if len(padded_encoded_data) % 8 != 0:
		#print("encoded data not padded properly")
		exit(0)
	
	b = bytearray()
	for i in range(0,len(padded_encoded_data),8):
		byte = padded_encoded_data[i:i + 8]
		b.append(int(byte,2))
	return b

def Huffman(path):
	img = cv2.imread(path)

	r, g, b = cv2.split(img)
	data, yinyang = make_data(r, g, b)
	shape = r.shape

	freq_dict = make_freq_dict(data)
	heap = make_heap(freq_dict)
	merge_node(heap)
	code_dict, recode_dict = make_code(heap)

	encoded_data = get_encoded_data(data, code_dict) 
	padded_encoded_data = pad_encoded_data(encoded_data)
	#print('img compressed')

	
	#write yinyang
	file_yinyang = open("yinyang.bin","wb")

	padded_yinyang = pad_encoded_data(yinyang)
	b_yinyang = get_byte_array(padded_yinyang)

	file_yinyang.write(b_yinyang)

	file_yinyang.close()
	

	#write shape
	result = []
	for ele in shape:
		ele1 = ele // 255
		ele2 = ele % 255
		result.append(ele1)
		result.append(ele2)
	
	file_shape = open("shape.bin","wb")
	file_shape.write(bytearray(result))
	file_shape.close()
	#print('shape written')

	#write recode_dict
	file_keys = open("keys.bin","wb")
	file_vals = open("vals.bin","wb")
	file_carry = open("carry.bin","wb")

	keys = list(recode_dict.keys())
	vals = list(recode_dict.values())
	carry = [len(str(ele)) for ele in keys]

	encoded_keys = ""
	for ele in keys:
		encoded_keys += ele
	
	
	padded_encoded_keys = pad_encoded_data(encoded_keys)
	b_keys = get_byte_array(padded_encoded_keys)

	file_keys.write(b_keys)
	file_vals.write(bytearray(vals))
	file_carry.write(bytearray(carry))

	file_keys.close()
	file_vals.close()
	file_carry.close()
	#print('recode_dict written')


	#write encoded_data
	file_compress = open('compress.bin',"wb")
	b = get_byte_array(padded_encoded_data)
	file_compress.write(b)
	#print('encoded_data written')


start = time.time()
Huffman('tower.jpg')
end = time.time() - start
print(end, ' s')