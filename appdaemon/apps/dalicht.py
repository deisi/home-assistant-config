"""Control lights"""
import appdaemon.plugins.hass.hassapi as hass
import datetime


class DaLicht(hass.Hass):
    turnedOnLights = {}

    def initialize(self):
        self.run_at_sunset(self.on_sunset, offset=-900)
        #self.run_at_sunrise(self.on_sunrise, offset=900)

    def on_sunset(self, kwargs):
        self.log("on_sunset called")
        if self.anyone_home():
            if self.get_state("switch.beamer") == "on":
                self.turn_on("scene.abends_ohne_wohnzimmer")
            else:
                self.turn_on("scene.abends")

    def on_sunrise(self, kwargs):
        self.log("on_sunrise called")
        self.turn_off("group.licht", transition=900)
