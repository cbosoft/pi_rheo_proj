import dig_pot
import time

dp = dig_pot.MCP4131()

for i in range(0,128):
    dp.set_resistance(i)
    time.sleep(1)