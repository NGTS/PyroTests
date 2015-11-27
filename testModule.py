# script to test the pyro setup
from collections import defaultdict
import Pyro4
import time
import threading

class moduleTest(object):

	def __init__(self):
		"""Sets up the test module"""
		self._running=True
		self._transp_time=time.time()
		self._cloud_time=time.time()
		self._rain_time=time.time()
		self._microphone_time=time.time()
		self._lock=threading.Lock()
		self.status=defaultdict(list)

	def startThread(self):
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
		else:
			print "Invalid thread_name"

	def run_transp_thread(self):
		while (self._running):
			self.status["transp"]=self.check(self._transp_time)
			print self.status["transp"]
			time.sleep(5)

	def run_cloud_thread(self):
		while (self._running):
			self.status["cloud"]=self.check(self._cloud_time)
			print self.status["cloud"]
			time.sleep(5)

	def run_rain_thread(self):
		while (self._running):
			self.status["rain"]=self.check(self._rain_time)
			print self.status["rain"]
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
		
	def check(self, chk):
		if (time.time() - chk) > 90: 
			return 0
		else:
			return 1

	def running(self):
		"""Returns True when daemon is running"""
		return self._running

	def stop(self):
		"""Stop the daemon thread"""
		self._running = False

daemon=Pyro4.Daemon('10.2.5.32')
test=moduleTest()
ns=Pyro4.locateNS()
uri=daemon.register(moduleTest)
ns.register('example.test',uri)
print ('Ready.')
daemon.requestLoop(loopCondition=test.running)
