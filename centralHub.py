# script to setup the central Pyro hub
# start name server with
# python -m Pyro4.naming -n IP
#
import Pyro4
import time
import threading

status={"Transparency":0,
		"Cloud Watcher":0,
		"Rain Sensors":0,
		"Microphones":0}

class centralHub(object):

	def __init__(self):
		"""Sets up the central hub"""
		self._running=True
		self._transp_time=time.time()
		self._cloud_time=time.time()
		self._rain_time=time.time()
		self._microphones_time=time.time()
		self._lock=threading.Lock()

	def startThread(self,thread_name):
		"""Start one of the various threads available"""
		if thread_name=="Transparency":
			transp_runloop=threading.Thread(target=self.run_transp_thread)
			transp_runloop.daemon=True
			transp_runloop.start()
		elif thread_name=="Cloud Watcher":
			cloud_runloop=threading.Thread(target=self.run_cloud_thread)
			cloud_runloop.daemon=True
			cloud_runloop.start()
		elif thread_name=="Rain Sensors":
			rain_runloop=threading.Thread(target=self.run_rain_thread)
			rain_runloop.daemon=True
			rain_runloop.start()
		elif thread_name=="Microphones":
			microphones_runloop=threading.Thread(target=self.run_microphones_thread)
			microphones_runloop.daemon=True
			microphones_runloop.start()
		elif thread_name=="Summary":
			summary_runloop=threading.Thread(target=self.run_summary_thread)
			summary_runloop.daemon=True
			summary_runloop.start()
		else:
			print("Invalid thread_name")

	def Td(self,text, class_id):
  		return "<td class=%s>%s</td>" % (class_id,text)

	def wrapRow(self,elements):
		return "<tr>%s</tr>" % (elements)

	def run_summary_thread(self):
		"""Thread summary thread"""
		global status
		outdir="/home/ops/ngts/prism/monitor"
		while(self._running):
			sum_str=""
			out_str=""
			tab_str="<table class='scripts_running'>"
			for i in status:
				sum_str=sum_str+"%s: %d " % (i,status[i])
				if status[i] == 1:
					class_str='goodqty'
				elif status[i] == 0:
					class_str='badqty'
				else:
					class_str='uknqty'
				out_str=out_str+self.Td(i,class_str)
			print (sum_str)
			tab_str=tab_str+self.wrapRow(out_str)+"</table>"
			f=open('%s/scripts_running.php' % (outdir),'w')
			f.write(tab_str)
			f.close()
			time.sleep(60)	

	def run_transp_thread(self):
		"""Transparency thread"""
		global status
		while (self._running):
			status["Transparency"]=self.check(self._transp_time,90)
			time.sleep(5)

	def run_cloud_thread(self):
		"""Cloudwatcher thread"""
		global status
		while (self._running):
			status["Cloud Watcher"]=self.check(self._cloud_time,90)
			time.sleep(5)

	def run_rain_thread(self):
		"""Rain sensor thread"""
		global status
		while (self._running):
			status["Rain Sensors"]=self.check(self._rain_time,90)
			time.sleep(5)

	def run_microphones_thread(self):
		"""Microphones thread"""
		global status
		while (self._running):
			status["Microphones"]=self.check(self._microphones_time,90)
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

	@Pyro4.oneway
	def update_microphone(self,t):
		"""Update the hand shake time of microphones script"""
		self._microphones_time=t

	def check(self,chk, timeout_time):
		"""Check the last update time"""
		if (time.time() - chk) > timeout_time: 
			return 0
		else:
			return 1
		
	def running(self):
		"""Returns True when daemon is running"""
		return self._running

	def stop(self,proc):
		"""Stop the daemon thread"""
		status[proc]=0
		self._running = False

def main():
	"""Wrap it all up"""
	daemon=Pyro4.Daemon('10.2.5.32')
	hub=centralHub()
	ns=Pyro4.locateNS()
	uri=daemon.register(centralHub)
	ns.register('central.hub',uri)
	print ('Ready.')
	hub.startThread('Summary')
	daemon.requestLoop(loopCondition=hub.running)

if __name__ == '__main__':
	main()
