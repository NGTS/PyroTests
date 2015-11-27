# script to setup the central Pyro hub
import Pyro4
import time
import threading

status={"transp":0,
		"cloud":0,
		"rain":0,
		"microphones":0}

class centralHub(object):

	def __init__(self):
		"""Sets up the central hub"""
		self._running=True
		self._transp_time=time.time()
		self._cloud_time=time.time()
		self._rain_time=time.time()
		self._microphone_time=time.time()
		self._lock=threading.Lock()

	def startThread(self,thread_name):
		"""Start one of the various threads available"""
		if thread_name=="transp":
			transp_runloop=threading.Thread(target=self.run_transp_thread)
			transp_runloop.daemon=True
			transp_runloop.start()
		elif thread_name=="cloud":
			cloud_runloop=threading.Thread(target=self.run_cloud_thread)
			cloud_runloop.daemon=True
			cloud_runloop.start()
		elif thread_name=="rain":
			rain_runloop=threading.Thread(target=self.run_rain_thread)
			rain_runloop.daemon=True
			rain_runloop.start()
		elif thread_name=="microphone":
			microphone_runloop=threading.Thread(target=self.run_microphone_thread)
			microphone_runloop.daemon=True
			microphone_runloop.start()
		elif thread_name=="summary":
			summary_runloop=threading.Thread(target=self.run_summary_thread)
			summary_runloop.daemon=True
			summary_runloop.start()
		else:
			print("Invalid thread_name")

	def run_summary_thread(self):
		"""Thread summary thread"""
		global status
		while(self._running):
			# print the status of all inputs
			sum_str=""
			for i in status:
				sum_str=sum_str+"%s: %d " % (i,status[i])
			print (sum_str)
			# update the html table 
			time.sleep(5)	

	def run_transp_thread(self):
		"""Transparency thread"""
		global status
		while (self._running):
			status["transp"]=self.check(self._transp_time,90)
			time.sleep(5)

	def run_cloud_thread(self):
		"""Cloudwatcher thread"""
		global status
		while (self._running):
			status["cloud"]=self.check(self._cloud_time,90)
			time.sleep(5)

	def run_rain_thread(self):
		"""Rain sensor thread"""
		global status
		while (self._running):
			status["rain"]=self.check(self._rain_time,90)
			time.sleep(5)

	@Pyro4.oneway
	def update_transp(self,t):
		"""Update the hand shake time of transparency script"""
		self._transp_time=t

	@Pyro4.oneway
	def update_cloud(self,t):
		"""Update the hand shake time of cloudwatcher script"""
		self._cloud_time=t

	@Pyro4.oneway
	def update_rain(self,t):
		"""Update the hand shake time of rain sensor script"""
		self._rain_time=t

	def check(self,chk, timeout_time):
		"""Check the last update time"""
		if (time.time() - chk) > timeout_time: 
			return 0
		else:
			return 1
		
	def running(self):
		"""Returns True when daemon is running"""
		return self._running

	def stop(self):
		"""Stop the daemon thread"""
		self._running = False

def main():
	"""Wrap it all up"""
	daemon=Pyro4.Daemon('10.2.5.32')
	hub=centralHub()
	ns=Pyro4.locateNS()
	uri=daemon.register(centralHub)
	ns.register('central.hub',uri)
	print ('Ready.')
	hub.startThread('summary')
	daemon.requestLoop(loopCondition=hub.running)

if __name__ == '__main__':
	main()
