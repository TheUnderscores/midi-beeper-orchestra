import sys
import midiparser
#sys.setdefaultencoding('binary')
print(sys.argv)
file = open(sys.argv[1],'rb')


filecontents = file.read()
midiparser.interpret_midi_data(filecontents)
