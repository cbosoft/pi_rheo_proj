import dig_pot
import time

dp = dig_pot.MCP4131()
try:
    for i in range(0,128):
        dp.write_byte(i)
        print "set to " + str(i)
        time.sleep(1)
    dp.write_byte(0)
    print "set to 0"
except KeyboardInterrupt:
    dp.close()
