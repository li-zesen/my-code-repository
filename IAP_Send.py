import crccheck
import os

def IAP_CRC(filepath, send_size=1024):
    # send_size : 每次发送的字节数
    # filepath : bin文件路径 
    # 'D:\\STM32 Projects\\Power_Control\\Debug Internal\\Power_Control.bin'

    # 打开bin文件
    binfile = open(filepath, 'rb') #打开二进制文件
    file_size = os.path.getsize(filepath) #获得文件大小
    file_data = binfile.read()
    binfile.close()
    
    # 发送数据的列表，一次一个
    send_list = []
    # 发送次数
    send_num = int(file_size/send_size)+1

    for i in range(send_num-1):
        data = file_data[i*send_size:(i+1)*send_size]
        crc_value = crccheck.crc.Crc32Mpeg2.calcbytes(data)
        send_list.append(data+crc_value)
    data = file_data[(send_num-1)*send_size:]
    crc_value = crccheck.crc.Crc32Mpeg2.calcbytes(data)
    send_list.append(data+crc_value)

    return send_list
