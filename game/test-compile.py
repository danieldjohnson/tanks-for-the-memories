import constants
import tank_ais
import sys

if __name__ == '__main__':
	try:
		tank_ais.AIManager(sys.argv[1], constants.WALLS)
	except tank_ais.SandboxCodeExecutionFailed, e:
		print e.args[0]