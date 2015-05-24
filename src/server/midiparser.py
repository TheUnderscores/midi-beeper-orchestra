import struct
import binascii
import convert

def parse_var_int(data,offset):
    nums = []
    total = 0
    while data[offset] & 0x80:
        print(data[offset])
        nums.append(data[offset] % 128)
        offset+=1
    print(data[offset])
    nums.append(data[offset] % 127)
    offset+=1
    print(nums)
    for num_i, num in enumerate(nums):
        total += num*((2**7)**(len(nums)-(num_i+1)))
    print(total)
    return (total,offset)
'''    delta_time = 0
    length = 1
    while (struct.unpack("@B",data[offset+length-1:offset+length])[0] & 0x80) > 0:
        #print("data[offset:offset+length] is {}\n{}\nOffset:{} Length:{}".format(data[offset:offset+length+1],binascii.hexlify(data),offset,length))
        length+=1
    for i in range(length):
        offset+=1
        inc = 0
        for char in data[0:offset+1]:
            delta_time += (char%128) << (7*inc)
            inc+=1
        offset+=1
    return (delta_time,offset)'''

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
            tracks.append(track)
            offset = 0
            #Event: [type,delay,hz]
            lasttype=0
            while offset < len(chunk[1]):
                delta_time,offset = parse_var_int(chunk[1],offset)
                typebyte = chunk[1][offset]
                offset+=1
                print("Typebyte {},offset {}".format(typebyte, offset))
                #running status bullshit
                if not (typebyte & 0x80):
                    typebyte = lasttype
                    print("CONTINUE:YES")
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
                    track.append([note_on,delta_time,convert.hzToMIDI(key)])
                else:
                    print("bad things happened. Possibly corrupt midi file")
                lasttype = typebyte
    return tracks

def process(data):
    tracks = interpret_midi_data(data)
    points = {}
    #pos = 0
    for track in tracks:
        pos = 0
        for event in track:
           pos+=event[1]
           if event[0] != 0:
               points.setdefault(pos,[]).append(event)
           else:
               print(event)
    s = sorted(points.items(),key=lambda x: x[0])
    num_on = 0
    max_on = 0
    print("A")
    for time,evlist in s:
        for ev in evlist:
            #print(ev)
            if ev[0]:
                num_on += 1
            else:
                num_on -= 1
                print("GOOD YAAY")
                exit()
            if num_on > max_on:
                max_on = num_on
    print("B")
#    biggest = 0
#    for pos,point in points.items():
#        print(len(point))
#        if len(point) > biggest:
#            biggest = len(point)
    print(max_on)
