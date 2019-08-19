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
logging.basicConfig(level=logging.DEBUG)
# Options DEBUG, INFO, WARNING, ERROR, CRITICAL

import HTU21D

update_interval  = 0.1 # seconds
display_interval = 0.5 # seconds

# Default constructor will pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.
#
# Optionally you can override the bus number:
#sensor = HTU21D.HTU21D(busnum=2)
sensor = HTU21D.HTU21D(logger='HTU21D.sensor')

lastUpdate  = time.time()
lastDisplay = time.time()

while True:
  currentTime = time.time()
  if currentTime - lastUpdate >= update_interval :
    sensor.update()
    lastUpdate = currentTime
  if ((currentTime - lastDisplay) >= display_interval):
    print("Temerature: %.1f deg C" % (sensor.temperature) ) 
    print("Humidity:   %.1f %% rH" % (sensor.humidity) )
  # release task
  timeRemaining = display_interval - (time.time() - currentTime)
  if (timeRemaining > 0):
    time.sleep(timeRemaining)
