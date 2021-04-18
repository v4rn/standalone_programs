
#------------- Tiny database restful api ----------------------------------
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
#		- Error checking in url_parser
#		- Error checking in query_parser
# 
# Notes: 
# 		- Overwrite the SIGINT handler to handle safe termination Ctrl+C/SIGINT
#		- Set the SERVER_RUNNING event variable to true. The SIGINT handler turns off this variable. The server's main while loop stops when this event variable is unset
#		- Currently the http request can only be 4096 bytes long
#
# Confusing things:
# 		- When using time cmd total time becomes smaller than user or sys time as # of multiple process go up
#		- listen has a backlog, number of failed connections should decrease with the backlog number, but it's the same
#		- Processes are I/O bound, does this affect the first point? 
#----------------------------------------------------------------------------
 
############# Testing notes ##################################################
# Used multiple processes in parallel making 10k GET requests in total
# Hardware specs: 1 processor, 2 cores, 4 logical cores (hyperthreading enabled)

# Requests	No. parallel processes		Request timeout		Failed Connections		Time elapsed(user, sys, real)
#--------------------------------------------------------------------------------------------------------------
#  10k				100						100ms				154						47,64,39 seconds
#  10k				 20						100ms				120						47,64,39 seconds
#  10k				 10						100ms				 65						46,64,45 seconds
#  10k				 04						100ms				 03						47,60,53 seconds
#  10k				 02						100ms				 02						29,49,66 seconds
#  10k				 01						100ms				 01						26,42,84 seconds
#  
#  10k				100						500ms				 87						47,64,39 seconds
#  10k				 20						500ms				 00						47,64,50 seconds
#  10k				 10						500ms				 00						47,63,54 seconds
#  10k				 04						500ms				 00						47,60,55 seconds
#  10k				 02						500ms				 00 					29,49,72 seconds
#  10k				 01						500ms				 00						26,43,84 seconds		
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

	SERVER_RUNNING.clear()				# Unset to disable the while loop in func basic_blocking server

	print("Created a local socket to close the server")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as close_socket:
		close_socket.connect(("",PORT))	# Make this connection to move from accept to while condition
##################################################

############ Simple in-memory ####################
database = {}
def set_key(key, value):	
	database[key] = value
	return {key : database[key]}		# After setting return {key:value} to notify success

def get_key(key,_):
	try:
		return {key : database[key]}	# if key present then return {key:value}
	except KeyError:					# ... else return {"KeyNotFound" : "InvalidOperation"}
		return {"KeyNotFound" : "InvalidOperation"}
																
def del_key(key,_):			
	try:						 
		return {key : database.pop(key)}	# if key present then return {key : pop_key_value}	
	except KeyError:						# ... else return {"KeyNotFound" : "InvalidOperation"}
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

	param_list = []								# convert params in the query string and return 
	for param in query.split("&"):				# ... a list of (key,value) tuples
		key_value = param.split("=")
		key = key_value[0]
		value = None if len(key_value) == 1 else key_value[-1]
		param_list.append((key, value))
	return param_list			

def url_parser(client_socket, http_data):
	logging.debug ("Data recevied: %s" %str(http_data))

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
	
	resp_dict = {}								# build the response dict using the query parser
	for param in query_parser(query):
		resp_dict.update(operation_dict[http_method](*param))

	resp = json.dumps(resp_dict)				# convert the python dictionary into a json string
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

		print ("Connected to client: %s" %str(client_addr))

		data = client_socket.recv(4096) 				# recv is blocking and stays connected to client 
														# ... even if no data is being sent, it unblocks when the 
														# ... client closes the connection
		print("\tRequest received: %s" %str(data))												
		if data: url_parser(client_socket, data)		# handle the get and post request

	server_socket.close()
##################################################

if __name__ == "__main__":
	print ("\nCheck server.log for debug information")

	logging.basicConfig(filename="server.log", 
						filemode="w", 					# log truncates at every run
						level=logging.DEBUG)

	print ("Overwriting SIGINT handler for proper clean up. Use Ctrl+C/SIGINT to request termination")
	signal.signal(signal.SIGINT, server_exit_handler)

	print ("Enabling server start event for synchronization\n")
	SERVER_RUNNING.set()
	
	print ("Running server localhost:%d ..." %PORT)
	basic_blocking_server(PORT)

	print ("\nExiting server ...")
