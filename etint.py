import audiotools
import threading
import Queue
import os
import sys

#FORMAT = pyaudio.paInt16
#CHANNELS = 1
#RATE = 8000
#CHUNK = 1024

HOME_DIR = os.path.dirname(os.path.realpath(__file__))

PLAYER_FILENAME  = HOME_DIR+"/audio/hschantShortPinkP.wav"
WORKER_FILENAME  = HOME_DIR+"/audio/hschantShortPinkW.wav"
MATCHER_FILENAME = HOME_DIR+"/audio/hschantShort.wav"
#PLAYER_FILENAME  = HOME_DIR+"/audio/playerD.wav"
#WORKER_FILENAME  = HOME_DIR+"/audio/workerD.wav"
#MATCHER_FILENAME = HOME_DIR+"/audio/matcherD.wav"

def main():	

	lock = threading.Lock()
	queue = Queue.Queue()

	#myLooper = audiotools.Looper(lock,queue,PLAYER_FILENAME,WORKER_FILENAME)
	#myLooper.play()

	print len(sys.argv)
	print sys.argv[1]
		
	if len(sys.argv) == 2:
		channel = int(sys.argv[1])
	else:
		channel = 0
	myMatcher = audiotools.Matcher(lock,queue,MATCHER_FILENAME,WORKER_FILENAME,PLAYER_FILENAME,channel)
	myMatcher.play()
	
	
		

if __name__ == '__main__':
	main()

#except (KeyboardInterrupt, SystemExit):
#	print "interuppted"
#	myMatcher.stop()
#	myLooper.stop()
#	sys.exit("Exited Program")
#	quit()


