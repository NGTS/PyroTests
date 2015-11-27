# script to test the pyro setup
import Pyro4
import time
import threading

class moduleTest(object):

	def __init__(self):
		"""Sets up the test module"""
		self._running=True
		self._t_time=time.time()
		self._lock=threading.Lock()

		transp_runloop=threading.Thread(target=self.run_transp_thread)
		transp_runloop.daemon=True
		transp_runloop.start()

	def run_transp_thread(self):
		while (self._running):
			stat=self.check(self._t_time)
			if stat == False:
				print "TIMEOUT"
			else:
				print "OK"
			time.sleep(5)

	def running(self):
		"""Returns True when daemon is running"""
		return self._running

	@Pyro4.oneway
	def update(self,t):
		self._t_time=t
		
	def check(self):
		if (time.time() - self._t_time) > 90: 
			return False
		else:
			return True

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
