from flask import *
import subprocess
import socket
import time
import os
import glob
import json
package_list = []
app = Flask(__name__)

@app.route('/stop/',methods=['POST'])
def stop():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.connect(('192.168.43.15', 4006)) 
	s.send(("stop").encode('utf-8'))
	s.close()
	return '', 200
@app.route('/download/',methods=['POST'])
def download():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.connect(('192.168.43.15', 4006)) 
	names = request.form['download_text']
	names = names.split(',')[0:-1]
	for i in range(len(names)):
		names[i] = int(names[i])
	for i in range(len(package_list)):
		if names[i]:
			print("{}".format(package_list[i]))
			s.send(("download "+(package_list[i][0])).encode('utf-8'))
			#s.bind(('192.168.43.15',4000))
			#s.listen(1)
			print("Waiting for response from server")
			flag = True
			while(flag):
				#accepting connection from client
				#clientsocket, addr = s.accept()
				print("Accepting connection!")
				print(int(package_list[i][1]))
				start = time.time()
				transfer = (s.recv(int(package_list[i][1])))
				end = time.time()
				time.sleep(2)
				f = open(package_list[i][0]+".zip",'wb')
				f.write(transfer)
				f.close()
				print("file created")
				print("time taken to download  {}".format(end-start))
				#clientsocket.close()
				flag = False
	s.close()
	return '', 200
@app.route('/')
def home():
	packages = subprocess.getoutput('dpkg -l').split('\n')[5:]
	pip_packages = subprocess.getoutput('pip list').split('\n')[2:-2]
	for i in range(0,len(packages)):
		packages[i] = packages[i][3:].split()
		packages[i][3] = ' '.join(packages[i][3:])
		packages[i] = packages[i][0:4]
	for i in range(len(pip_packages)):
		pip_packages[i] = pip_packages[i].split()

	#Listing available packages in server

	# creating a socket to listen for incoming connections
	hello_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = 4006
	hello_socket.connect(('192.168.43.15',port))
	hello_socket.send(("hello").encode('utf-8'))

	for i in range(2):
		m = hello_socket.recv(500).decode('utf-8').split(" ")
		package_list.append(m)
	hello_socket.close()

	check_box = []
	for i in range(len(package_list)):
		check_box.append(0)
		for pkg in packages:
			if package_list[i][0] in pkg[0]:
				check_box[i] = 1
				break
		if check_box[i]!=1:
			for pkg in pip_packages:
				if package_list[i][0] in pkg[0]:
					check_box[i] = 1
					break

	return render_template("main.html",packages=packages,pip_packages=pip_packages,package_list=package_list,check_box=check_box)

if __name__ == '__main__':
	app.run(debug=True)


