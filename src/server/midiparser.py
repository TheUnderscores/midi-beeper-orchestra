import struct

def parse_var_int(data,offset):
    while (struct.unpack("@B",chunk[offset][0:1])[0] & 0x80) > 0:
        offset+=1
        delta_time = 0
        inc = 0
        for char in chunk[1][0:offset+1]:
            delta_time += (char%128) << (7*inc)
            inc+=1
    return (detla_time,offset)

def interpret_midi_data(data):
    """
    Takes in the contents of a midi file and spits out an array of tracks with notes in them
    """
    offset = 0
    mode = 0 #0: reading chunk type, 1: reading length, 2: reading chunk data
    chunks = [] # data.__len__
    while offset < len(data):
        chunktype = data[offset:offset+4]
        offset+=4
        chunklength = struct.unpack(">L", data[offset:offset+4])[0]
        offset+=4
        print("Chunktype {}, length {}".format(chunktype,chunklength))
        chunk = data[offset:offset+chunklength]
        chunks.append([chunktype,chunk])
        offset+=chunklength
    #Read header
    header = chunks.pop(0)
    chunkdata = header[1]
    print(len(header[1]))
    midi_format = struct.unpack(">H", chunkdata[0:2])
    num_tracks = struct.unpack(">H", chunkdata[2:4])
    division = struct.unpack(">H", chunkdata[4:6])
    tracks = []
    #Everything else
    for chunk in chunks:
        print(chunk[0])
        if chunk[0] == b"MTrk":
            track = []
            tracs.append(track)
            offset = 0
            #Event: [type,delay,note_num]
            while offset < len(chunk[1]):
                delta_time,offset = parse_var_int(chunk[1],offset)
                typebyte = chunk[1][offset]
                offset+=1
                nibble = typebyte >> 4
                if typebyte == 0xF0 || typebyte == 0xF7:
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
                elif nibble == 0xC || nibble == 0xD:
                    #single-byte messages we dont care about
                    track.append([0,delta_time])
                    offset += 1
                elif nibble == 0xA || nibble == 0xB || nibble == 0xE:
                    #dual-byte messages we don't care about
                    track.append([0,delta_time])
                    offset += 2
                elif nibble == 0x8 || nibble == 0x9:
                    channel = typebyte & 0x0F
                    key = chunk[1][offset]
                    velocity = chunk[1][offset+1]
                    note_on = nibble==0x09
                    if(note_on && velocity == 0):
                        note_on = false
                    track.append([note_on,delta_time,key])
                else:
                    print("bad things happened. Possibly corrupt midi file")
    return tracks
