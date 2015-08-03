import os
import wave
import threading
import sys
import shutil
import pyaudio
import audioop
import time

LOOPER_CHUNK = 8000
INPUT_CHUNK = 1024
FORMAT = pyaudio.paInt16
BYTES = 2
CHANNELS = 1
RATE = 8000


class Looper(threading.Thread) :
  """
  A simple class based on PyAudio to play wave loop.

  It's a threading class. You can play audio while your application
  continues to do its stuff. :)
  """

  def __init__(self, lock, q, filepath_player, filepath_worker, CHUNK=LOOPER_CHUNK) :
    """
    Initialize `Looper` class.

    PARAM:
        -- 
        -- filepath_worker (String) : File Path to file to play.
        -- filepath_player (String) : File Path to file being built.
        -- loop (boolean)    : True if you want loop playback. 
                               False otherwise.
    """
    super(Looper, self).__init__()
    #self.daemon = True
    self.lock = lock
    self.queue = q
    self.filepath_player = os.path.abspath(filepath_player)
    self.filepath_worker = os.path.abspath(filepath_worker)
    self.loop = True
    self.CHUNK = LOOPER_CHUNK

    self.audio_interface = pyaudio.PyAudio()
    self.audio_output = self.audio_interface.open(
      format = FORMAT,
      channels = CHANNELS,
      rate = RATE,
      output = True)
    self.player_wav = wave.open(self.filepath_player, 'rb')

  def run(self):
    # PLAYBACK LOOP
    data = self.player_wav.readframes(self.CHUNK)
    while self.loop :

      self.audio_output.write(data)
      data = self.player_wav.readframes(self.CHUNK)

      #sys.stdout.write('.')
      #sys.stdout.flush()
      # Get new player data
      if data == '' : # If file is over then rewind.
        #sys.stdout.write('\n')
        self.player_wav.close()
        self.queue.put("writedata")
        self.queue.join()

        self.lock.acquire()
        #shutil.copyfile(self.filepath_worker,self.filepath_player)
        self.player_wav = wave.open(self.filepath_player,'rb')
        self.lock.release()

        data = self.player_wav.readframes(self.CHUNK)

  def play(self) :
    """
    Just another name for self.start()
    """
    self.start()

  def stop(self) :
    """
    Stop playback. 
    """
    print "Stopping Playback"
    self.loop = False
    self.player_wav.close()
    self.audio_output.stop_stream()
    self.audio_output.close()
    self.audio_interface.terminate()

class Matcher(threading.Thread):
  def __init__(self, lock, q, filepath_matcher, filepath_worker, filepath_player,in_channel=0):
    super(Matcher, self).__init__()
    self.daemon = True
    self.lock = lock
    self.queue = q
    self.filepath_matcher = os.path.abspath(filepath_matcher)
    self.filepath_worker = os.path.abspath(filepath_worker)
    self.filepath_player = os.path.abspath(filepath_player)
    self.in_channel = in_channel
    #More arguments here if needed
    self.SEGMENT = 5  #5 seconds
    self.OFFSET = 0
    self.TIMING = 0
    self.WAV_LENGTH = 0
    self.BYTES = 2
    self.LOCAL_CHUNK = INPUT_CHUNK/4

    self.audio_interface = pyaudio.PyAudio()

    #List Audio Devices
    for i in range(0, self.audio_interface.get_device_count()):
      print str(i) + " " + self.audio_interface.get_device_info_by_index(i)["name"]
      pass

    self.audio_input = self.audio_interface.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=self.in_channel,
                        frames_per_buffer=INPUT_CHUNK)

    # Open and read filedata
    # Open wave file
    mf = wave.open(self.filepath_matcher, 'rb')
    self.FRAMES = mf.getnframes()
    self.WAV_LENGTH = self.FRAMES*BYTES
    self.wavdata = mf.readframes(self.FRAMES)
    self.params = mf.getparams()
    mf.close()

    # Get New Worker Info
    self.lock.acquire()
    wf = wave.open(self.filepath_worker,'rb')
    self.workdata = wf.readframes(self.FRAMES)
    wf.close()
    self.lock.release()
    # print "worklen "+str(len(self.workdata))

  def run(self):
    #print "Started input"
    while True:
      #print "loop"
      if not self.queue.empty():
        message = self.queue.get()
        if message == "writedata":
          print "Writing Data"
          print "Acquire Lock"
          self.lock.acquire()
          wfo = wave.open(self.filepath_player, 'wb')
          wfo.setparams(self.params)

          print "Writing "+str(len(self.workdata))+" BYTES"
          wfo.writeframes(self.workdata)
          wfo.writeframes('')

          print "Releasing Lock"
          wfo.close()
          self.lock.release()
          self.queue.task_done()
      
      # Main writing loop
      else:
        # Get New Mic Info
        try:
          micdata = self.audio_input.read(self.LOCAL_CHUNK)
          #sys.stdout.write('*')
          #sys.stdout.flush()
        except:
          print "***** Ignored oveflow *****" 
          pass

        in_pos  = self.OFFSET*BYTES
        out_pos = in_pos+(self.SEGMENT*RATE*BYTES)
        if out_pos > self.WAV_LENGTH:
          out_pos = self.WAV_LENGTH

        seg_wavdata = self.wavdata[in_pos:out_pos]
        seg_workdata = self.workdata[in_pos:out_pos]

        point, factorM = audioop.findfit(seg_wavdata,micdata)
        seg_in_pos = point*2
        seg_out_pos = seg_in_pos+len(micdata)
        offst, factorW = audioop.findfit(seg_wavdata[seg_in_pos:seg_out_pos],seg_workdata[seg_in_pos:seg_out_pos])

        #print "Searched ("+str(in_pos)+", "+str(out_pos)+")" 
        #print "len "+str(len(self.wavdata))
        #print "format "+str(BYTES)

        if factorM > 0:
          if abs(1-factorM) < abs(1-factorW):
            print "Matched @ " + str((in_pos+seg_in_pos)) + ", with factor:" + str(factorM)

            #micpart = audioop.mul(micdata,2,(factorM*0.9))
            #workpart = audioop.mul(seg_workdata[seg_in_pos:seg_out_pos],2,0.1)
          #else:
            #print "WeakMat @ " + str((in_pos+seg_in_pos)) + ", with factor:" + str(factorM)

            #micpart = audioop.mul(micdata,2,(factorM*0.1))
            #workpart = audioop.mul(seg_workdata[seg_in_pos:seg_out_pos],2,0.9)

            msg = []
            msg.append(self.workdata[0:in_pos])
            msg.append(seg_workdata[0:seg_in_pos])
            msg.append(micdata)
            #msg.append(audioop.add(micpart,workpart,BYTES))
            msg.append(seg_workdata[seg_out_pos:len(seg_workdata)])
            msg.append(self.workdata[out_pos:self.WAV_LENGTH])

            self.workdata = b''.join(msg)
          #print "new work len "+str(len(self.workdata))

        #Increment Chunk
        self.TIMING += 1
        if self.TIMING > 100:
          # Then move offset
          self.OFFSET = self.OFFSET+(self.SEGMENT*RATE)
          if out_pos == self.WAV_LENGTH:
            self.OFFSET = 0
          # And Reset TIMING
          self.TIMING =0

  def play(self):
    self.start()

  def stop(self) :
    """
    Stop playback. 
    """
    print "Stopping Input"
    self.audio_input.stop_stream()
    self.audio_input.close()
    self.audio_interface.terminate()






    