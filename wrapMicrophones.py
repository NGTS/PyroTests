# script to wrap up the microphones in python
import Pyro4
import time, os, sys
import threading
import signal

class ffserver(object):

	def __init__(self):
		"""Sets up the ffserver class"""
		self._running=True
		self._lock=threading.Lock()

	def startThread(self,thread_name):
		"""Start one of the various threads available"""
		if thread_name=="ffserver":
			ffserver_runloop=threading.Thread(target=self.run_ffserver_thread)
			ffserver_runloop.daemon=True
			ffserver_runloop.start()
		elif thread_name=="pyro":
			pyro_runloop=threading.Thread(target=self.run_pyro_thread)
			pyro_runloop.daemon=True
			pyro_runloop.start()
		else:
			print("Invalid thread_name")

	def run_ffserver_thread(self):
		"""Run the ffserver in a separate thread"""
		os.popen('/usr/local/bin/ffserver -f /home/ops/ngts/ffserver/ffserver.conf')

	def run_pyro_thread(self):
		"""Run the pyro in a separate thread"""
		ping_microphone=Pyro4.Proxy("PYRONAME:central.hub")
		ping_microphone.startThread("Microphones")
		while(self._running):
			ping_microphone.update_microphone(time.time())
			print ("checking in...")
			time.sleep(10)

	def stop(self):
		"""Stop the daemon thread"""
		self._running = False
	
# set up Ctrl+C handling
die=False
def signal_handler(signal,frame):
	global die
	print "Ctrl+C caught, exiting..."
	die=True

signal.signal(signal.SIGINT,signal_handler)

def main():
	ff=ffserver()
	ff.startThread("ffserver")
	py=ffserver()	
	py.startThread("pyro")

	while(1):
		time.sleep(5)
		# close up 		
		if die == True:
			ff.stop()
			print ("Stopping ffserver")
			py.stop()
			print ("Stopping pyro")
			sys.exit(1)

if __name__ == '__main__':
	main()
