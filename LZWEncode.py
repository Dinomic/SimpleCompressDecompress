import numpy
import cv2
import matplotlib.pyplot as plt
import time
def get_image_rgb(image_name):
	pic = cv2.imread(image_name)
	return cv2.cvtColor(pic,cv2.COLOR_BGR2RGB)


def show_image_gray(image_gray):
	plt.imshow(image_gray,cmap = "gray")
	plt.show()


def split_image(image_rgb):
	return cv2.split(image_rgb)


def ravel_image(image_gray):
	return image_gray.ravel()


def get_initial_table(data):
	table = dict()
	code = 0
	for ele in data:
		flag = table.setdefault(ele,code)
		if flag == code:
			code += 1
	return table


def write_keys(table,channel):
	keys = list(table.keys())
	file_keys = open("keys" + str(channel) + ".bin","wb")
	file_keys.write(bytearray(keys))
	file_keys.close()
	#print("channel: %d" % (channel),"keys written")


def write_values(table,channel):
	values = list(table.values())
	file_values = open("values" + str(channel) + ".bin","wb")
	file_values.write(bytearray(values))
	file_values.close()
	#print("channel: %d" % (channel),"values written")


def get_man_data(data):
	return [str(ele) for ele in data]


def get_man_table(initial_table):
	table = dict()
	for keys in initial_table:
		table.setdefault(str(keys),initial_table.get(keys))
	return table


def encoding(data,initial_table):
	data = get_man_data(data)
	table = get_man_table(initial_table)
	code = len(table)
	start = data[0]
	data = data[1:]
	output = list()
	for ele in data:
		next = ele
		if table.get(start + " " + next,-1) != -1:
			start = start + " " + next
		else:
			output.append(table.get(start))
			table.setdefault(start + " " + next,code)
			code += 1
			start = next
	output.append(table.get(start))
	return output


def adapt_encoded(encoded):
	result = list()
	for ele in encoded:
		ele_1 = ele // (255 * 255)
		ele_2 = ele % (255 * 255) // 255
		ele_3 = ele % (255 * 255) % 255
		result.extend([ele_1,ele_2,ele_3])
	return result


def adaptive_encode(image_shape):
	result = list()
	for ele in image_shape:
		ele_1 = ele // 255
		ele_2 = ele % 255
		result.extend([ele_1,ele_2])
	return result


def write_encoded(encoded,channel):
	file_encoded = open("encoded" + str(channel) + ".bin","wb")
	file_encoded.write(bytearray(encoded))
	file_encoded.close()
	#print("channel: %d" % (channel),"encoded")


def run():
	#image_name = input("image_gray_name: ")
	image_name = "tower.jpg"
	
	image_rgb = get_image_rgb(image_name)
	r,g,b = split_image(image_rgb)
	channels = [r,g,b]
	
	for i in range(3):
		data = ravel_image(channels[i])
		initial_table = get_initial_table(data)
	
		write_keys(initial_table,i)
		write_values(initial_table,i)
	
		encoded = encoding(data,initial_table)
		final = adapt_encoded(encoded)
	
		write_encoded(final,i)
	
	""" write shape """
	
	shape = r.shape
	
	shape_encoded = adaptive_encode(shape)
	
	file_shape = open("shape.bin","wb")
	file_shape.write(bytearray(shape_encoded))
	file_shape.close()
	
	#print("shape written")


if __name__ == "__main__":
	start = time.time()
	run()
	end = time.time() - start
	print(end, ' s')
	"""data = [1,2,1,2,2,1,2,3,1,2,1,2,2,1]
	initial_table = get_initial_table(data)
	
	write_keys(initial_table)
	write_values(initial_table)
	
	encoded = encoding(data,initial_table)
	
	write_encoded(encoded)
	
	file_read = open("encoded.bin","rb")
	print(list(file_read.read()))
	file_read.close()
	
	result = adapt_encoded(encoded)
	print(result)"""


















