import pymedia.audio.acodec
import pymedia.muxer
import time, wave, string, os
import sys

def convertToWav(inFileName):
  '''Converts a file to wav format.

   Returns the name of the newly created wav file.
   '''

  inFileBase, inFileExt = os.path.splitext(inFileName)
  if inFileExt.startswith('.'):
    inFileExt = inFileExt[1:]
    
  outFileName = inFileBase + '.wav'

  # Open demuxer first

  demuxer = pymedia.muxer.Demuxer(inFileExt)
  decoder = None
  inFile = open(inFileName, 'rb')
  outFile = None
  bufSize = 20000

  buf = inFile.read(bufSize)
  while buf:
    frames = demuxer.parse(buf)
    for frame in frames:
      if decoder == None:
        # Open decoder
        decoder = pymedia.audio.acodec.Decoder(demuxer.streams[0])
      r = decoder.decode(frame[1])
      if r and r.data:
        if outFile == None:
          outFile = wave.open(outFileName, 'wb')
          params = (r.channels,
                    2,
                    r.sample_rate,
                    0,
                    'NONE',
                    '')
          outFile.setparams(params)
        outFile.writeframes(r.data)
    buf = inFile.read(bufSize)

  return outFileName  

#-------------------------------------------------------------------
if __name__ == '__main__':

  convertToWav(sys.argv[1])
