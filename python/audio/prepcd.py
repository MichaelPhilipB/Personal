import splitwav
import converttowav
import sys
import os

#-------------------------------------------------------------------
def prepCd(inFileName):
    '''Prepares an audio file to become a CD.

     Converts it to .wav (if necessary) and splits it into tracks.
     '''

    base, ext = os.path.splitext(inFileName)
    if ext.startswith('.'):
        ext = ext[1:]

    if ext not in ['mp3', 'wav']:
        print 'Error: "' + str(ext) + '" is not a valid file extension.'
        sys.exit(1)

    if ext == 'mp3':
        print "Converting to wav..."
        inFileName = converttowav.convertToWav(inFileName)

    print 'Spliting file...'
    splitwav.splitWav(inFileName)

#-------------------------------------------------------------------
if __name__ == '__main__':
    
  args = sys.argv[1:]

  if len(args) == 1:
    prepCd(args[0])
  else:
    print """Usage:  prepcd in_file_name

Takes the input mp3/wav file and splits it into several smaller wav files.
"""
    sys.exit( 1 )
