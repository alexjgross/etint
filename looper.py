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

  def __init__(self,filepath_player, filepath_worker, CHUNK=LOOPER_CHUNK) :
    super(Looper, self).__init__()
    self.filepath_player = os.path.abspath(filepath_player)
    self.filepath_worker = os.path.abspath(filepath_worker)
    self.loop = True
    self.CHUNK = LOOPER_CHUNK

    self.audio_interface = pyaudio.PyAudio()
    self.audio_output = self.audio_interface.open(
      format = FORMAT,
      channels = CHANNELS,
      rate = RATE,
      output_device_index = 1,
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
      
        self.player_wav = wave.open(self.filepath_player,'rb')

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