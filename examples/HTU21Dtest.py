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

# Can enable debug output by uncommenting:
import logging
logging.basicConfig(level=logging.ERROR)
# Options DEBUG, INFO, WARNING, ERROR, CRITICAL

import HTU21D.HTU21D as HTU21D

# Default constructor will pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.
#
sensor = HTU21D.HTU21D()

# Optionally you can override the bus number:
#sensor = HTU21D.HTU21D(busnum=2)
temperature = sensor.read_temperature()
humidity = sensor.read_humidity()
print("Temp: %s C" % temperature)
print("Humid: %s %% rH" % humidity)
print("Humid C: %s %% rH" % sensor.temp_coefficient(humidity, temperature))
      
