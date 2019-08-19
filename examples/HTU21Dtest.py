#!/usr/bin/python
# Author: Urs Utzinger
##
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time

# Can enable debug output by uncommenting:
import logging
logging.basicConfig()
# Options DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.getLogger().setLevel(logging.DEBUG)

import HTU21D
poll_interval = 0.1 # seconds
loop_interval = 0.001 # seconds

# Default constructor will pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.
#
# Optionally you can override the bus number:
#sensor = HTU21D.HTU21D(busnum=2)
sensor = HTU21D.HTU21D(logger='HTU21D.sensor')

lastPoll=time.time()
previousRateTime=time.time()
humidityCounter=0

while True:
  currentTime = time.time()
  if currentTime - lastPoll >= poll_interval :
    # temperature = sensor.read_temperature()
    humidity,temperature = sensor.read_humidity()
    print("Temp: %.2f deg C" % temperature)
    print("Humid: %.2f %% rH" % humidity)
    humidityCounter += 1
  if ((currentTime - previousRateTime) >= 1.0):
    humidityRate = humidityCounter
    humidityCounter = 0
    previousRateTime = currentTime
    print("Humidity rate: %d" % (humidityRate) ) 
  # release task
  timeRemaining = loop_interval - (time.time() - currentTime)
  if (timeRemaining > 0):
    time.sleep(timeRemaining)
