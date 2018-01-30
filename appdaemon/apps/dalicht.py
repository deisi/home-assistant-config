"""Control lights"""
import appdaemon.appapi as appapi


class DaLicht(appapi.AppDaemon):
    def initialize(self):
        self.run_at_sunset(self.on_sundown)
        self.run_at_sunrise(self.on_sunrise)

    def on_sunset(self, kwargs):
        if self.get_state(self.args["people"]) == "home":
            if self.get_state("switch.beamer") == "on":
                self.turn_on("scene.abends_ohne_wohnzimmer")
            else:
                self.turn_on("scene.abends")

    def on_sunrise(self, kwargs):
        self.turn_off("group.licht")

