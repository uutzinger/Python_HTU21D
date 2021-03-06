try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

setup(name              = 'HTU21D',
      version           = '1.0.0',
      author            = 'Urs Utzinger',
      author_email      = 'uutzinger@gmail.com',
      description       = 'Library for accessing the HTU21D humidity and temperature sensor',
      license           = 'MIT',
      classifiers       = classifiers,
      url               = 'https://github.com/uutzinger/Python_HTU21D/',
      dependency_links  = ['https://github.com/uutzinger/Adafruit_Python_GPIO.git'],
      install_requires  = ['Adafruit_GPIO>=1.0.4'],
      packages          = find_packages())
