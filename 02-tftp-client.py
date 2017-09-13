from socket import *
import struct
import sys


def downLoad(fileName,udpSocket):
	
	#total packages number
	total_num = 0
	f = open("./"+fileName,"ba")
	while True:
		#recevfrom:(data,endpoint)-----------tuple
		recvdata,EndPoint = udpSocket.recvfrom(1024)

		pkg_header = struct.unpack("!HH",recvdata[0:4])
		oper_num = pkg_header[0]
		cur_pkg_num = pkg_header[1]

		#package is normal
		if oper_num == 3:
			
			if total_num+1 == cur_pkg_num:
				f.write(recvdata[4:])
				ack_pkg = struct.pack("!HH",4,cur_pkg_num)
				udpSocket.sendto(ack_pkg,EndPoint)
				total_num += 1
			
			if len(recvdata) < 516:
				print("---------------download finish----------------")
				f.close()

				break
		#error
		if oper_num == 5:
			print("error number:%d"%oper_num)
			f.close()
			
			break

		if len(recvdata) == 0:
			break
	udpSocket.close()


def main():
	if len(sys.argv) != 3:
		print("add server IP and file name")
		sys.exit()
	
	serverIP = sys.argv[1]
	fileName = sys.argv[2]
	fileName_len = str(len(fileName))
	
	#first request send to server
	requestData = struct.pack("!H"+fileName_len+"sb5sb",1,fileName.encode("utf-8"),0,"octet".encode("utf-8"),0)
	
	udpSocket = socket(AF_INET,SOCK_DGRAM)
	udpSocket.bind(("192.168.238.138",24195))
	udpSocket.sendto(requestData,(serverIP,69))
	
	downLoad(fileName,udpSocket)
	

if __name__ == '__main__':
	main()
	sys.exit()