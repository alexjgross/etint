import audiotools
import threading
import Queue
import os

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
	try:
		myLooper = audiotools.Looper(lock,queue,PLAYER_FILENAME,WORKER_FILENAME)
		myLooper.play()

		myMatcher = audiotools.Matcher(lock,queue,MATCHER_FILENAME,WORKER_FILENAME,1)
		myMatcher.play()
	except:
		print "Something happened, check you are using the correct input."
		pass

if __name__ == '__main__':
    main()