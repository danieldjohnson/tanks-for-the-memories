from sandbox_utils.RestrictedPython import compile_restricted
import sandbox_utils.ZopeGuards as ZopeGuards
import sandbox_utils.ZopeReplacements as ZopeReplacements

ZopeGuards.initialize(ZopeReplacements)
get_safe_globals = ZopeGuards.get_safe_globals
guarded_getattr = ZopeGuards.guarded_getattr

import os, signal, copy, traceback, sys
from contextlib import contextmanager
from numbers import Number
from pprint import pprint

EXECUTION_TIMEOUT = 0.1

class SandboxCodeExecutionFailed(Exception):
	pass

class SandboxCodeExecutionTimeout(Exception):
	pass

def _sandbox_timeout_handler(signum, frame):
	raise SandboxCodeExecutionTimeout("Running the AI took too long!")

@contextmanager
def sandbox_timeout(timeout):
	oldhandler = signal.signal(signal.SIGALRM, _sandbox_timeout_handler)
	try:
		signal.setitimer(signal.ITIMER_REAL, timeout)
		yield
	finally:
		signal.setitimer(signal.ITIMER_REAL, 0)
		signal.signal(signal.SIGALRM, oldhandler)

class AIManager(object):
	"""
	Class that wraps a sandboxed AI implementation
	"""

	def __init__(self, path, initstate):
		with open(path) as f:
			text = f.read()

		self.name = os.path.basename(path)
		try:
			self.code = compile_restricted(text, os.path.basename(path), 'exec')

			self.sbxglobals = get_safe_globals()
			self.sbxglobals['_getattr_'] = guarded_getattr
			self.sbxglobals['_print_'] = self.getLogger
			self.sbxglobals['__name__'] = __name__ # so classes can be defined in the script

			with sandbox_timeout(EXECUTION_TIMEOUT):
				exec self.code in self.sbxglobals
				# pprint(self.sbxglobals)
				self.ai_obj = self.sbxglobals['TankAI']()
				self.ai_obj.init(copy.deepcopy(initstate))

		except BaseException:
			raise SandboxCodeExecutionFailed(self.fix_sandbox_exception())

	def getLogger(self):
		class LoggerHelper(object):
			def write(self2, string):
				self.log(string)
		return LoggerHelper()

	def log(self, string):
		print "FROM {}: {}".format(self.name, string)

	def fix_sandbox_exception(self):
		print "--- orig exc"
		print traceback.format_exc()
		print "---"
		tb_parts = traceback.extract_tb(sys.exc_traceback)
		exc_only = traceback.format_exception_only(sys.exc_type, sys.exc_value)
		filtered_tb_parts = [part for part in tb_parts if part[0] == self.name]

		filtered_tb = ["Traceback (most recent call last):\n"]
		filtered_tb += traceback.format_list(filtered_tb_parts)
		filtered_tb += exc_only
		return ''.join(filtered_tb)

	def doTurn(self, state):
		try:
			with sandbox_timeout(EXECUTION_TIMEOUT):
				action = self.ai_obj.doTurn(copy.deepcopy(state))

		except BaseException:
			self.log(self.fix_sandbox_exception())
			action = ("pass",)

		# Verify desired move
		if action is None:
			return ("pass",)
		elif action == ("pass",) or (action[0] == "move" and isinstance(action[1], Number)):
			return action
		else:
			self.log("Invalid action {}".format(action))
			return ("pass",)
