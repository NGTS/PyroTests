# script to setup the central Pyro hub
from collections import defaultdict
import Pyro4
import time
import threading

class centralHub(object):

	def __init__(self):
		"""Sets up the central hub"""
		self._running=True
		self._transp_time=time.time()
		self._cloud_time=time.time()
		self._rain_time=time.time()
		self._microphone_time=time.time()
		self._lock=threading.Lock()
		self.status={"transp":0,
					"cloud":0,
					"rain":0,
					"microphones":0}

	def startThread(self,thread_name):
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
			print "Invalid thread_name"

	def run_summary_thread(self):
		while(self._running):
			# print the status of all inputs
			sum_str=""
			for i in self.status:
				self_str=self_str+"%s: %d" % (i,self_status[i])
			# update the html table 
			time.sleep()	

	def run_transp_thread(self):
		while (self._running):
			self.status["transp"]=self.check(self._transp_time,90)
			time.sleep(5)

	def run_cloud_thread(self):
		while (self._running):
			self.status["cloud"]=self.check(self._cloud_time,90)
			time.sleep(5)

	def run_rain_thread(self):
		while (self._running):
			self.status["rain"]=self.check(self._rain_time,90)
			time.sleep(5)

	@Pyro4.oneway
	def update_transp(self,t):
		self._transp_time=t

	@Pyro4.oneway
	def update_cloud(self,t):
		self._cloud_time=t

	@Pyro4.oneway
	def update_rain(self,t):
		self._rain_time=t
		
	def check(self, chk, timeout_time):
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
	daemon=Pyro4.Daemon('10.2.5.32')
	hub=centralHub()
	ns=Pyro4.locateNS()
	uri=daemon.register(centralHub)
	ns.register('central.hub',uri)
	print ('Ready.')
	daemon.requestLoop(loopCondition=hub.running)

if __name__ == '__main__':
	main()
