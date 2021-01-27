import cv2
import numpy as np
import time
def decode_shape (shape_encoded):
	return [shape_encoded[0] * 255 + shape_encoded[1],shape_encoded[2] * 255 + shape_encoded[3]]

def remove_padding(padded_encoded_data):
    padded_info = padded_encoded_data[:8]
    extra_padding= int(padded_info, 2)
    padded_encoded_data =padded_encoded_data[8:]
    encoded_data = padded_encoded_data[:-1 * extra_padding]
    return encoded_data

def decode_data(encoded_data, recode_dict, yinyang):
    current_code = ""
    decoded_data = list()
    for bit in encoded_data:
        current_code += bit
        if current_code in recode_dict:
            val = recode_dict[current_code]
            decoded_data.append(val)
            current_code = ""

    for i in range(1,len(decoded_data)):
        if yinyang[i-1]  == '0':
            decoded_data[i] = decoded_data[i-1] - decoded_data[i]
        else:
            decoded_data[i] = decoded_data[i-1] + decoded_data[i]
    #print(len(decoded_data))
    return decoded_data

def decompress():
    #shape decode
    file_shape = open("shape.bin","rb")
    shape_encoded = list(file_shape.read())
    shape = decode_shape(shape_encoded)
    file_shape.close()

    #recode_dict decode
    file_keys = open('keys.bin', 'rb')
    file_val = open('vals.bin', 'rb')
    file_carry = open('carry.bin', 'rb')

    bit_string = ''
    byte = file_keys.read(1)
    while len(byte) != 0:
        byte = ord(byte)
        bits = bin(byte)[2:].rjust(8, '0')
        bit_string += bits
        byte = file_keys.read(1)
    keys_string = remove_padding(bit_string)

    carry = list(file_carry.read())
    vals = list(file_val.read())
    keys = list()

    for ele in carry:
        keys.append(keys_string[:ele])
        keys_string = keys_string[ele:]

    recode_dict = dict()
    for i in range(len(keys)):
        recode_dict[keys[i]] = vals[i]

    file_carry.close()
    file_keys.close()
    file_val.close()

    #yinyang decode
    file_yinyang = open('yinyang.bin', 'rb')

    bit_string = ''
    byte = file_yinyang.read(1)
    while len(byte) != 0:
        byte = ord(byte)
        bits = bin(byte)[2:].rjust(8, '0')
        bit_string += bits
        byte = file_yinyang.read(1)

    yinyang = remove_padding(bit_string)
    #print(len(yinyang))
    
    file_yinyang.close()

    #data decode
    file_data = open('compress.bin','rb')
    bit_string =''
    byte = file_data.read(1)
    while len(byte) != 0:
        byte = ord(byte)
        bits = bin(byte)[2:].rjust(8, '0')
        bit_string += bits
        byte = file_data.read(1)
    data_string = remove_padding(bit_string)
    
    decoded_data = decode_data(data_string, recode_dict, yinyang)
    
    #print(len(decoded_data))
    mark1 = int(len(decoded_data)/3)
    #print(mark1)
    mark2 = int(mark1*2)
    #print(mark2)

    rr = decoded_data[:mark1]
    gg = decoded_data[mark1:mark2]
    bb = decoded_data[mark2:]

    chanels = list()
    r = np.reshape(rr,shape).astype('uint8')
    chanels.append(r)
    g = np.reshape(gg,shape).astype('uint8')
    chanels.append(g)
    b = np.reshape(bb,shape).astype('uint8')
    chanels.append(b)

    pic = cv2.merge((chanels))

    return pic

    #print('abc')

start = time.time()
img = decompress()
cv2.imshow('wala', img)
end = time.time() - start
print(end, ' s')
#print('abc')

cv2.waitKey()
cv2.destroyAllWindows()