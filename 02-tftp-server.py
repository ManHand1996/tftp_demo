import socket
import struct
import os
import random
#socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSERADDR,1)
#-------------------------------------------------
#		  2byte  n/2 bytes   1byte  5byte  1byte
#请求格式：1/2 + file_name + 0 + octec + 0
#数据包： 3 + package_num + 512 bytes（data）
#ACK: 4 + package_num
#ERROR 5 + error_num + error_msg + 0
#-------------------------------------------------


#1.接受客户端的请求(请求格式),根据请求格式进行对应操作
#2.如果是请求下载：
	#检测文件名存在
	#若存在，将文件分成若干个数据包。。。
	#等待客户端答复，判断，再继续发一下数据包


udpServerSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#接受请求端口
udpServerSock.bind(("192.168.238.140",69))

print("start!")
while True:
	requestData,clientEndPoint = udpServerSock.recvfrom(1024)
	#print("step 1")
	if requestData is not None:
		
		oper_num = struct.unpack("!H",requestData[0:2])
		oper_num = oper_num[0]
		# 0 + octec + 0
		last_data = struct.unpack("!b5sb",requestData[-7:])
		last_data = str(last_data[0])+str(last_data[1],"utf-8")+str(last_data[2])

		name_length = len(requestData) - 9
		file_name = struct.unpack("!"+str(name_length)+"s",requestData[2:-7])
		file_name = str(file_name[0],"utf-8")#bytes to unicode

		# print(file_name)
		# print(clientEndPoint)
		# print(last_data)
		# print(oper_num)
		if oper_num == 1:

			#download
			#if file is exist send 
			#if not  send error 5
			if os.path.exists("./"+file_name):
				f = open("./"+file_name,"br")
				pkg_num = 0
				while True:
					newPort = random.randint(20000,30000) + 1
					print("new Port:%s"%newPort)

					#socket close后 需要重新创建再绑定，否则会出现：bad file descriptor
					#socket 没有close而直接重新绑定，会出现：invalid arguament
					sendSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
					sendSocket.bind(("192.168.238.140",newPort))
					
					fileData = f.read(512)
					print("len file:%s"%len(fileData))
					
					if not fileData:
						f.close()
						print("finish")
						break
					#打包
					pkg_num += 1
					data_pkg = struct.pack("!HH"+str(len(fileData))+"s",3,pkg_num,fileData)
					
					sendSocket.sendto(data_pkg,clientEndPoint)
					ACK_pkg = sendSocket.recvfrom(1024)[0]
					#拆包：
					ACK_NUM,curr_pkg_num = struct.unpack("!HH",ACK_pkg[:4]) 
					
					#print("ack num:%d"%ACK_NUM) 
					#print("package num:%d"%curr_pkg_num)
					
					if ACK_NUM == 4 and curr_pkg_num == pkg_num:
						#print("close 1")
						sendSocket.close()
						continue
					else:
						f.close()
						print("----------error----------")
						break

udpServerSock.close()