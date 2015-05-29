import struct
import binascii
import convert
import manager

def parse_var_int(data,offset):
    nums = []
    total = 0
    while data[offset] & 0x80:
        nums.append(data[offset] % 128)
        offset+=1
    nums.append(data[offset] % 127)
    offset+=1
    for num_i, num in enumerate(nums):
        total += num*((2**7)**(len(nums)-(num_i+1)))
    return (total,offset)

def interpret_midi_data(data):
    """
    Takes in the contents of a midi file and spits out an array of tracks with notes in them
    """
    offset = 0
    mode = 0 #0: reading chunk type, 1: reading length, 2: reading chunk data
    chunks = []
    while offset < len(data):
        chunktype = data[offset:offset+4]
        offset+=4
        chunklength = struct.unpack(">L", data[offset:offset+4])[0]
        offset+=4
        chunk = data[offset:offset+chunklength]
        chunks.append([chunktype,chunk])
        offset+=chunklength
    #Read header
    header = chunks.pop(0)
    chunkdata = header[1]
    midi_format = struct.unpack(">H", chunkdata[0:2])
    num_tracks = struct.unpack(">H", chunkdata[2:4])
    division = struct.unpack(">H", chunkdata[4:6])
    tracks = []
    #Everything else
    for chunk in chunks:
        if chunk[0] == b"MTrk":
            track = []
            tracks.append(track)
            offset = 0
            #Event: [type,delay,hz]
            lasttype=0
            while offset < len(chunk[1]):
                delta_time,offset = parse_var_int(chunk[1],offset)
                typebyte = chunk[1][offset]
                offset+=1
                #running status bullshit
                if not (typebyte & 0x80):
                    typebyte = lasttype
                    offset-=1
                nibble = typebyte >> 4
                if typebyte == 0xF0 or typebyte == 0xF7:
                    #sysex event, skip
                    event_length,offset = parse_var_int(chunk[1],offset)
                    track.append([0,delta_time])
                    offset+=event_length #skip over these
                elif typebyte == 0xFF:
                    #Meta event, skip
                    meta_type = chunk[1][0]
                    offset+=1
                    track.append([0,delta_time])
                    event_length,offset = parse_var_int(chunk[1],offset)
                    offset += event_length
                elif nibble == 0xC or nibble == 0xD:
                    #single-byte messages we dont care about
                    track.append([0,delta_time])
                    offset += 1
                elif nibble == 0xA or nibble == 0xB or nibble == 0xE:
                    #dual-byte messages we don't care about
                    track.append([0,delta_time])
                    offset += 2
                elif nibble == 0x8 or nibble == 0x9:
                    channel = typebyte & 0x0F
                    key = chunk[1][offset]
                    velocity = chunk[1][offset+1]
                    note_on = nibble==0x09
                    if(note_on and velocity == 0):
                        note_on = False
                    bla = 2
                    if note_on:
                        bla = 1
                    print(key)
                    hz = 0
                    if key > 0:
                        hz = convert.MIDItoHz(key)
                    track.append([bla,delta_time,hz])
                lasttype = typebyte
    return tracks

def process(data,num_layers):
    tracks = interpret_midi_data(data)
    layers_notes = []
    layers_timing =[]
    layers = []
    for bla in range(num_layers):
        layers_notes.append(0)
        layers_timing.append(0)
        layers.append(manager.Layer())
    notes_playing = {}
    normalized_tracks = []
    points = {}
    for track in tracks:
        pos = 0
        for event in track:
           pos+=event[1]
           if event[0] > 0:
               points.setdefault(pos,[]).append(event)
    
    s = sorted(points.items(),key=lambda x:x[0])
    for time,events in s:
        for event in events:
            #first find a layer that isn't busy
            if event[0] == 1:
                layer_to_use = -1
                for i in range(len(layers_notes)):
                    if layers_notes[i] == 0:
                        layer_to_use = i
                        break
                if layer_to_use == -1:
                    print("WARNING: wasn't able to allocate space for event")
                else:
                    layers[layer_to_use].addEvent(manager.Event((time-layers_timing[layer_to_use])*500,event[2]))
                    layers_notes[i] = event[2]
                    layers_timing[layer_to_use] = time
            elif event[0] == 2:
                layer_to_use = -1
                for i in range(len(layers_notes)):
                    if layers_notes [i] == event[2]:
                        layer_to_use = i
                layers[layer_to_use].addEvent(manager.Event((time-layers_timing[layer_to_use])*500,0))
                layers_notes[layer_to_use] = 0
                layers_timing[layer_to_use] = time

    return layers
