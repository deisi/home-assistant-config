"""App to control presence related tasks."""
import appdaemon.appapi as appapi

class DaHause(appapi.AppDaemon):

    def initialize(self):
        self.listen_state(self.on_home_entered,
                          self.args["people"], new="home")
        self.listen_state(self.on_home_left,
                          self.args["people"], new="not_home")

    def on_home_entered(self):
        if self.sun_down():
            self.turn_on(self.args["lights_on"])
        self.turn_on(self.args["switches_on"])

    def on_home_left(self):
        self.turn_off(self.args["lights_off"])
        self.turn_off(self.args["switches_off"])
        self.call_service(
            "media_player/media_play_pause",
            entity_id=self.args["mediaplayer_off"]
        )
