"""
Support for Projectors from Acer.

"""
import logging
import re

import voluptuous as vol

from homeassistant.components.media_player import(
    SUPPORT_TURN_ON, SUPPORT_TURN_OFF, SUPPORT_SELECT_SOURCE, PLATFORM_SCHEMA,
    SUPPORT_VOLUME_STEP, SUPPORT_PLAY_MEDIA, SUPPORT_PLAY, MediaPlayerDevice,
)
from homeassistant.const import (
    STATE_ON, STATE_OFF, STATE_UNKNOWN, CONF_NAME, CONF_FILENAME,
    SERVICE_VOLUME_UP, SERVICE_VOLUME_DOWN)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pyserial==3.1.1']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Acer Projector'
DEFAULT_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 1

SUPPORT_ACER = SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE |\
               SUPPORT_VOLUME_STEP | SUPPORT_PLAY_MEDIA | SUPPORT_PLAY

CONF_TIMEOUT = 'timeout'
CONF_WRITE_TIMEOUT = 'write_timeout'

ICON = 'mdi:projector'

QUERY_ECO_MODE = 'ECO Mode'
QUERY_INPUT_SOURCE = 'Input Source'
QUERY_LAMP = 'Lamp'
QUERY_LAMP_HOURS = 'Lamp Hours'
QUERY_MODEL = 'Model'
QUERY_DISPLAY_RESOLUTION = 'Display Resolution'

SET_ECO_MODE = 'Set ECO Mode'
SOURCE_ANALOGE_RGB = 'Analoge RGB'
SOURCE_DIGITAL_RGB = 'Digital RGB'
SOURCE_PBPR = 'PbPr'
SOURCE_SVIDEO = 'S-Video'
SOURCE_COMPOSITE_VIDEO = 'Composite Video'
SOURCE_COMPONENT_VIDEO = 'Component Video'
SOURCE_HDMI = 'HDMI'

# Commands known to the projector
CMD_DICT = {
    QUERY_LAMP: '* 0 Lamp ?\r',
    QUERY_LAMP_HOURS: '* 0 Lamp\r',
    QUERY_INPUT_SOURCE: '* 0 Src ?\r',
    QUERY_ECO_MODE: '* 0 IR 052\r',
    QUERY_MODEL: '* 0 IR 035\r',
    QUERY_DISPLAY_RESOLUTION: '* 0 IR 036\r',
    SET_ECO_MODE: '* 0 IR 051\r',
    SERVICE_VOLUME_UP: '* 0 IR 023\r',
    SERVICE_VOLUME_DOWN: '* 0 IR 024 \r',
    SOURCE_HDMI: '* 0 IR 050\r',
    SOURCE_ANALOGE_RGB: '* 0 IR 015\r',
    SOURCE_DIGITAL_RGB: '* 0 IR 016\r',
    SOURCE_PBPR: '* 0 IR 017\r',
    SOURCE_SVIDEO: '* 0 IR 018\r',
    SOURCE_COMPOSITE_VIDEO: '* 0 IR 019\r',
    SOURCE_COMPONENT_VIDEO: '* 0 IR 020\r',
    STATE_ON: '* 0 IR 001\r',
    STATE_OFF: '* 0 IR 002\r',
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_FILENAME): cv.isdevice,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
    vol.Optional(CONF_WRITE_TIMEOUT, default=DEFAULT_WRITE_TIMEOUT):
        cv.positive_int,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Connect with serial port and return Acer Projector."""
    serial_port = config.get(CONF_FILENAME)
    name = config.get(CONF_NAME)
    timeout = config.get(CONF_TIMEOUT)
    write_timeout = config.get(CONF_WRITE_TIMEOUT)

    add_devices([AcerSwitch(serial_port, name, timeout, write_timeout)])


class AcerSwitch(MediaPlayerDevice):
    """Represents an Acer Projector as Media Player."""

    def __init__(self, serial_port, name, timeout, write_timeout, **kwargs):
        """Init of the Acer projector."""
        import serial
        self.ser = serial.Serial(
            port=serial_port, timeout=timeout, write_timeout=write_timeout,
            **kwargs)
        self._serial_port = serial_port
        self._name = name
        self._state = False
        self._available = False
        self._state_attributes = {
            QUERY_LAMP_HOURS: STATE_UNKNOWN,
            QUERY_INPUT_SOURCE: STATE_UNKNOWN,
            QUERY_ECO_MODE: STATE_UNKNOWN,
            QUERY_MODEL: STATE_UNKNOWN,
            QUERY_DISPLAY_RESOLUTION: STATE_UNKNOWN,
        }
        self._source_list = [
            SOURCE_ANALOGE_RGB, SOURCE_DIGITAL_RGB, SOURCE_PBPR, SOURCE_SVIDEO,
            SOURCE_COMPOSITE_VIDEO, SOURCE_COMPONENT_VIDEO, SOURCE_HDMI
        ]
        self._current_source = STATE_UNKNOWN,
        self.update()

    def _write_read(self, msg):
        """Write to the projector and read the return."""
        import serial
        ret = ""
        # Sometimes the projector won't answer for no reason or the projector
        # was disconnected during runtime.
        # This way the projector can be reconnected and will still work
        try:
            if not self.ser.is_open:
                self.ser.open()
            msg = msg.encode('utf-8')
            self.ser.write(msg)
            # Size is an experience value there is no real limit.
            # AFAIK there is no limit and no end character so we will usually
            # need to wait for timeout
            ret = self.ser.read_until(size=20)
            ret = ret.decode('utf-8', 'ignore')
        except serial.SerialException:
            _LOGGER.error('Problem comunicating with {}'.format(self._serial_port))
        self.ser.close()
        return ret

    def _write_read_format(self, msg):
        """Write msg, obtain awnser and format output."""
        # awnsers are formated as ***\rawnser\r***
        awns = self._write_read(msg)
        match = re.search(r'\r(.+)\r', awns)
        if match:
            return match.group(1)
        return STATE_UNKNOWN

    @property
    def available(self):
        """Return if projector is available."""
        return self._available

    @property
    def name(self):
        """Return name of the projector."""
        return self._name

    @property
    def is_on(self):
        """Return true if the projector is turned on."""
        return self._state

    @property
    def state(self):
        """Return state."""
        if self._state:
            return STATE_ON
        return STATE_OFF

    @property
    def state_attributes(self):
        """Return state attributes."""
        return self._state_attributes

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ACER

    @property
    def source_list(self):
        """Return list of input sources"""
        return self._source_list

    @property
    def source(self):
        """Name of the current source"""
        current_source = self._state_attributes.get(QUERY_INPUT_SOURCE)
        if "Src 0" in current_source or "Src 8" in current_source:
            current_source = SOURCE_HDMI
        return current_source

    def update(self):
        """Get the latest state from the projector."""
        msg = CMD_DICT[QUERY_LAMP]
        awns = self._write_read(msg)
        if 'Lamp 1' in awns:
            self._state = True
            self._available = True
        elif 'Lamp 0' in awns:
            self._state = False
            self._available = True
        else:
            self._available = False

        for key in self._state_attributes:
            msg = CMD_DICT.get(key, None)
            if msg:
                awns = self._write_read_format(msg)
                self._state_attributes[key] = awns

    def turn_on(self):
        """Turn the projector on."""
        msg = CMD_DICT[STATE_ON]
        self._write_read(msg)
        self._state = STATE_ON

    def turn_off(self):
        """Turn the projector off."""
        msg = CMD_DICT[STATE_OFF]
        self._write_read(msg)
        self._state = STATE_OFF

    def volume_up(self):
        """Volume up"""
        msg = CMD_DICT[SERVICE_VOLUME_UP]
        self._write_read(msg)

    def volume_down(self):
        """Volume down"""
        msg = CMD_DICT[SERVICE_VOLUME_DOWN]
        self._write_read(msg)

    def select_source(self, source):
        """Select input source."""
        msg = CMD_DICT.get(source, '')
        self._write_read(msg)

    def media_play(self):
        msg = CMD_DICT[STATE_ON]
        self._write_read(msg)

    def media_pause(self):
        msg = CMD_DICT[STATE_OFF]
        self._write_read(msg)

    def play_media(self, media_type, media_id, **kwargs):
        pass
