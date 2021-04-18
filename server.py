
#------------- Tiny database restful api ----------
# Python version: 3.7.3
# Usage: python server.py
# Client request:
#		Add/Update: curl -X POST "localhost:8080/?a=4&b=5"
#				    stores {'a' : 4, 'b' : 5}
# 		Remove:     curl -X DELETE "localhost:8080/?a"
#		Read:		curl "localhost:8080/?a"
#
# Improvements: 
#		- Testing with select(polling)
#		- Testing with async
# 
# Notes: 
# 		- Overwrite the sigint handler to handle safe termination Ctrl+C/SIGINT
#		- Set the SERVER_RUNNING event variable to true. The SIGINT handler turns off this variable. The server's main while loop stops when this event variable is unset
#		- Currently the http request can only be 4096 bytes long
#--------------------------------------------------
 
############# Testing notes ##################################################
# Used curl to multiple processes in parallel making 10k GET requests in total
##############################################################################

import socket
import signal
import threading
import os
import logging							# NOTE: thread-safe
import json

############### Global vars ######################
SERVER_RUNNING = threading.Event()		   # Event
PORT		   = 8080
##################################################

############### SIGINT handler ###################
def server_exit_handler(signum, frame):
	print("\n\nSignal handler SIGINT invoked - SIGNUM : %d" %signum)
	print("Working on closing file descriptors safely. Please wait ...")

	SERVER_RUNNING.clear()

	print("Created a local socket to close the server")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as close_socket:
		close_socket.connect(("",PORT))
##################################################

############ Simple in-memory ####################
database = {}
def set_key(key, value):	
	database[key] = value
	return {key : database[key]}

def get_key(key,_):
	return {key : database.get(key, "KeyNotFound")}

def del_key(key,_):			
	try:						 
		return {key : database.pop(key)}
	except KeyError:
		return {"KeyNotFound" : "InvalidOperation"}
							
##################################################

################## HTML/HTTP #####################
HTTP_OK_RESPONSE = """HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {body_size}

{body}""".format
##################################################

################## URL PARSER ####################
def query_parser(query):
	# example query string
	# POST 			method >> a=1&b=5&c=10
	# GET/DELETE 	method >> a&b&c

	param_list = []
	for param in query.split("&"):
		key_value = param.split("=")
		key = key_value[0]
		value = None if len(key_value) == 1 else key_value[-1]
		param_list.append((key, value))
	return param_list

def url_parser(client_socket, http_data):
	print("Data recevied: ",http_data)

	http_method = http_data.split()[0].decode().upper()
	url_path  	= http_data.split()[1].decode()
	query 	  	= url_path[url_path.find('?')+1:]
		
	# build a check valid routine here
	logging.debug ("HTTP data: %s" %http_data)
	
	operation_dict = { 	
						# http_methods  : func call to database

						"DELETE" 		: del_key,
						"POST"	 		: set_key,
						"GET"	 		: get_key,
					}
	
	resp_dict = {}
	for param in query_parser(query):
		print(param)
		resp_dict.update(operation_dict[http_method](*param))

	resp = json.dumps(resp_dict)
	client_socket.sendall(HTTP_OK_RESPONSE(body_size = len(resp.encode()), body = resp).encode()) 
##################################################

######### Basic blocking server ##################
def basic_blocking_server(port):
	server_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('',port))
	server_socket.listen()								# socket.SOMAXCONN is 128

	while SERVER_RUNNING.is_set():
		client_socket, client_addr = server_socket.accept()
		logging.debug ("Connected to client: %s" %str(client_addr))

		data = client_socket.recv(4096) 				# recv is blocking and stays connected to client 
														# ... even if no data is being sent, it unblocks when the 
														# ... client closes the connection
		if data: url_parser(client_socket, data)		# handle the get and post request
	server_socket.close()
##################################################

if __name__ == "__main__":
	logging.basicConfig(filename="server.log", filemode="w", level=logging.DEBUG)

	print ("Overwriting SIGINT handler")
	signal.signal(signal.SIGINT, server_exit_handler)

	print ("Enabling server start event")
	SERVER_RUNNING.set()
	
	print ("Running server localhost:%d" %PORT)
	basic_blocking_server(PORT)

	print ("\nExiting server ...")
