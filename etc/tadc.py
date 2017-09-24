from time import sleep 
from adc import MCP3008

adc = MCP3008(vref=3.3)
#adc.open()
#command = [1, (0x09 << 4), 0, 0, 0, 0]
#command = 0b11 << 6
#command |= (1 & 0x07) << 3
#command = [ command, 0, 0]
#print "command: ", command
#indat = adc.bus.xfer2(command)
#adc.close()
#print "bytes: ", indat
#for by in indat:
#    print "  {:b}".format(by)
#i = 0.0
#for j in range(0, len(indat)):
#    i += int(indat[j]) * 2**(len(indat) - 1 - j)
#print "ints: ", i#((indat[1] & 3) << 8) + indat[2]
#print "volts: ",  i * (3.3 / 1023)#(((indat[1] & 3) << 8) + indat[2]) * (3.3 / 1023)
#adares = (indat[0] & 0x01) << 9
#adares |= (indat[1] & 0xFF) << 1
#adares |= (indat[2] & 0x80) >> 7
#print "adafruit: ", adares
#print "adavolt: ", adares * (3.3 / 1023)
for i in range(0, 100):
    str_ = ""
    for j in range(0, 8):
        str_ += "|    c{}: {:.2f}    ".format(j, adc.read_volts(j))
    print str_
    sleep(1)
