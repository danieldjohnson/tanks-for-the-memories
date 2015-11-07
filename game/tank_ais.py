from config import *

from sandbox_utils.RestrictedPython import compile_restricted
import sandbox_utils.ZopeGuards as ZopeGuards
import sandbox_utils.ZopeReplacements as ZopeReplacements

ZopeGuards.initialize(ZopeReplacements)
get_safe_globals = ZopeGuards.get_safe_globals
guarded_getattr = ZopeGuards.guarded_getattr

import os
if not USE_SIMULATOR:
    import signal
import copy
import traceback
import sys
import datetime
from contextlib import contextmanager
from numbers import Number
from pprint import pprint

from config import *
if USE_SIMULATOR:
    import js, json

import constants
ZopeReplacements.import_mapping["constants"] = constants

EXECUTION_TIMEOUT = 0.1
MAX_LOG_SIZE = 100000

class SandboxCodeExecutionFailed(Exception):
    pass

class SandboxCodeExecutionTimeout(Exception):
    pass

def _sandbox_timeout_handler(signum, frame):
    raise SandboxCodeExecutionTimeout("Running the AI took too long!")

@contextmanager
def sandbox_timeout(timeout):
    if USE_SIMULATOR:
        yield
    else:
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

    def __init__(self, path, initstate, print_to_log=True):
        with open(path) as f:
            text = f.read()

        self.print_to_log = print_to_log
        self.logbuffer = []
        self.name = os.path.basename(path)
        self.idnum = self.name[:-3]
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

            self.flushlog()
        except BaseException:
            raise SandboxCodeExecutionFailed(self.fix_sandbox_exception())

    def getLogger(self):
        class LoggerHelper(object):
            def write(self2, string):
                self.log(string)
        return LoggerHelper()

    def log(self, string):
        if self.print_to_log:
            self.logbuffer.append(string)
        else:
            print string,

    def flushlog(self):
        if USE_SIMULATOR:
            js.globals.handle_log(self.ID, json.dumps(self.logbuffer))
        else:
            logfile = "../data/{}_out.log".format(self.idnum)
            with open(logfile, 'a') as f:
                f.writelines(self.logbuffer)
            size = os.path.getsize(logfile)
            if size > MAX_LOG_SIZE:
                os.remove(logfile)
                with open(logfile, 'a') as f:
                    f.write("...\n(truncated {})\n".format(datetime.datetime.today()))

        self.logbuffer = []

    def fix_sandbox_exception(self):
        tb_parts = traceback.extract_tb(sys.exc_traceback)
        exc_only = traceback.format_exception_only(sys.exc_type, sys.exc_value)
        filtered_tb_parts = [part for part in tb_parts if part[0] == self.name]

        filtered_tb = ["Traceback (most recent call last):\n"]
        filtered_tb += traceback.format_list(filtered_tb_parts)
        filtered_tb += exc_only
        return ''.join(filtered_tb)

    def takeTurn(self, state):
        try:
            with sandbox_timeout(EXECUTION_TIMEOUT):
                action = self.ai_obj.takeTurn(copy.deepcopy(state))

        except BaseException:
            self.log(self.fix_sandbox_exception())
            action = [[0,0],False,[0,0]]

        self.flushlog()

        # Verify desired move
        if action is None:
            return [[0,0],False,[0,0]]
        elif isinstance(action,list):
            if isinstance(action[0],list) and isinstance(action[1],bool) and isinstance(action[2],list):
                if len(action[0]) >= 2 and len(action[2]) >= 2:
                    return action
        else:
            self.log("Invalid action {}".format(action))
            return [[0,0],False,[0,0]]
