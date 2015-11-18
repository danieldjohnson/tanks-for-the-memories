from config import *

if USE_SIMULATOR:
	class ServerCommunicator(object):
		def __init__(self):
			"""There is no server in simulator mode."""
			pass
		def death_event(self, *args):
			pass

else:
	import zmq
	class ServerCommunicator(object):
		def __init__(self):
			ctx = zmq.Context()
			self.sock = ctx.socket(zmq.REQ)
			self.sock.connect('tcp://127.0.0.1:{}'.format(ZMQ_PORT))

		def death_event(self, killer_ID, killed_ID):
			self.sock.send_json(['death', killer_ID, killed_ID])
			return self.sock.recv()
