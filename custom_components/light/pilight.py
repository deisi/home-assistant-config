""" add support fo pilight lights"""
import logging
import subprocess

from homeassistant.components.light import ATTR_BRIGHTNESS, DOMAIN
#from homeassistant.external.pswitch.codesend_client import codesend
#from homeassistant.external.pilight.pdb import idToCode
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.helpers.entity import ToggleEntity

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """ Find and return pilight lights. """
    lights = []
    for name, cmds in config["cmdDict"].items():
        lights.append( Pilight(config["protocol"], name, cmds) )
    add_devices_callback(lights)

class Pilight(ToggleEntity):
    """PswitchLight obj"""

    def __init__(self, protocol, name, cmds):
        self.state_attr = {ATTR_FRIENDLY_NAME: name }
        self.status = False
        if protocol == "raw":
            self.setOn = "".join(["/usr/local/bin/pilight-send -p raw -c \"", cmds[0], "\""])
            self.setOff = "".join(["/usr/local/bin/pilight-send -p raw -c \"", cmds[1], "\""])

        #self.brightness = 0

    @property
    def name(self):
        return self.state_attr[ATTR_FRIENDLY_NAME]

    def turn_on(self, **params):
        """turn on the switch"""
        self.status = True
        subprocess.call(self.setOn, shell=True)

    def turn_off(self, **parmas):
        """turn of the switch"""
        self.status = False
        subprocess.call(self.setOff, shell=True)

    @property
    def is_on(self):
        """ True if switch is on"""
        return self.status
