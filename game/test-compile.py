import maps
import tank_ais
import sys

if __name__ == '__main__':
	try:
		tank_ais.AIManager(sys.argv[1], maps.just_walls, print_to_log=False)
	except tank_ais.SandboxCodeExecutionFailed, e:
		print e.args[0]