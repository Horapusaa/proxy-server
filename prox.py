#!/usr/bin/env python 
import os
import socket
import sys
import thread
print("enter the port : ")
port1=input()
config = {
			"QUEUE" : 50,				# pending connections
			"MAX_BYTES" : 999999,		# maximum bytes allowed to be received
			"DEBUG" : True,				# this is set to tru to see debug messages
			"BLOCKED" : ["codeforces.com"]				# for no blocking use BLOCKED =[""]
		}

def start():
	if len(sys.argv)<2:
		print "Using default port : 8080 (http-alt)"
		port = port1

	else:
		port = int(sys.argv[1])

	host = ''	# left blank for localhost

	print "Proxy server running on ",host,":",port
	
	try:
		s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(config["QUEUE"])

	except socket.error , (value, message):
		if s:
			s.close()

		print "Could not open socket:", message
		sys.exit(1)

	while True:
		try :
			conn, client_addr = s.accept()

			thread.start_new_thread(pr_thread , (conn, client_addr) )

		except KeyboardInterrupt :
			print "\nClosing server..."
			s.close()
			sys.exit(1)

	s.close()

def prnt(typ , request , addr):
	if "Block" in typ or "Blacklist" in typ:
		colornum = 91
	elif "Request" in typ:
		colornum = 92
	elif "Reset" in typ:
		colornum = 93

	print "\033[",colornum,"m",addr[0],"\t",typ,"\t",request,"\033[0m"	

def pr_thread(conn, addr):
	request = conn.recv(config["MAX_BYTES"])
	first_line = request.split('\n')[0]
	url = first_line.split(' ')[1]

	for i in range(len(config["BLOCKED"])):
		if config["BLOCKED"][i] in url:
			prnt("Blacklisted" , first_line , addr)
			conn.close()
			sys.exit(1)

	prnt("Request",first_line,addr)
	flag = url.find("://")

	if flag == -1:
		tmp = url

	else :
		tmp = url[flag+3:]

	port_pos = tmp.find(":")
	serv_pos = tmp.find("/")

	if serv_pos == -1:
		serv_pos = len(tmp)

	webserver = ""
	port = -1

	if port_pos == -1 or serv_pos < port_pos:
		port = 80
		webserver = tmp[:serv_pos]

	else:
		port = int( (tmp[port_pos+1:])[:serv_pos-port_pos-1] )
		webserver = tmp[:port_pos]

	try:
		s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
		s.connect((webserver,port))
		s.send(request)

		while True:
			data = s.recv(config["MAX_BYTES"])
			if len(data)>0:
				conn.send(data)
			else:
				break

	except socket.error, (value,message):
		if s:
			s.close()
		if conn:
			conn.close()
		prnt("Peer reset" , first_line , addr)
		sys.exit(1)

if __name__ == "__main__":
	start()
