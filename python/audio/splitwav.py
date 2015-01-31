import wave
import sys
import os.path

#-------------------------------------------------------------------
def splitWav(inFileName):
  '''Reads the specified file, and writes it split into chunks.

  Good for splitting up a long radio show into tracks for listening
  as a CD in the car.
  '''

  inFileBaseName, inFileExt = os.path.splitext(inFileName)
  inFile = wave.open(inFileName, 'rb')

  #print 'channels:', inFile.getnchannels()
  #print 'sample width'

  #print 'frames:      ', inFile.getnframes()
  #print 'comp:        ', inFile.getcompname()
  #print 'channels:    ', inFile.getnchannels()
  #print 'samplewidth: ', inFile.getsampwidth()
  #print 'framerate:   ', inFile.getframerate()

  framesPerSec = inFile.getframerate()
  bytesPerFrame = inFile.getnchannels() * inFile.getsampwidth()
  #print 'bytes/frame: ', bytesPerFrame

  secsPerFile = 300
  framesPerFile = framesPerSec * secsPerFile

  num = 1
  frames = inFile.readframes( framesPerFile )

  while frames:
    fileName = '%s_%02d.wav' % (inFileBaseName, num)
    num += 1

    numBytes = len(frames)
    secs = float(numBytes ) / bytesPerFrame  / framesPerSec
    print "Writing file %s with %d secs." % (fileName, secs)

    outfile = wave.open(fileName, 'wb')
    outfile.setparams(inFile.getparams())
    outfile.writeframes(frames)

    frames = inFile.readframes(framesPerFile)


#-------------------------------------------------------------------
if __name__ == '__main__':
    
  args = sys.argv[1:]

  if len(args) == 1:
    splitWav(args[0])
  else:
    print """Usage:  splitwav in_file_name

Takes the input wav file and splits it into several smaller wav files.
"""
    sys.exit( 1 )
    


