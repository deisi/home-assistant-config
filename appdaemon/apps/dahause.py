"""App to control presence related tasks."""
import appdaemon.plugins.hass.hassapi as hass

class DaHause(hass.Hass):

    def initialize(self):
        self.listen_state(self.on_home_entered,
                          self.args["people"], new="home")
        self.listen_state(self.on_home_left,
                          self.args["people"], new="not_home")

    def on_home_entered(self, entity, attribute, old, new, kwargs):
        self.log("on_home_entered called")
        if self.sun_down():
            self.log("Sun is down.")
            self.turn_on("group.licht")
            self.turn_on("scene.abends")
        self.turn_on(self.args["switches_on"])
        temp = float(self.get_state(entity="sensor.dark_sky_temperature"))
        if temp < self.args["heizung_min_val"]:
            self.log("Brrr its cold. Turn on heating for you.")
            self.call_service(
                "climate/set_operation_mode",
                entity_id=self.args["heizung_on"],
                operation_mode="Heat"
               )
        self.turn_off("switch.relay_1_2")
        self.turn_on("media_player.denon")
        self.call_service(
            'media_player/select_source',
            entity_id='media_player.denon',
            source='CD',
            )

        self.run_in(
            lambda x: self.call_service(
                'media_player/volume_set',
                entity_id='media_player.denon',
                volume_level=0.5,
            ),
            4,
        )


    def on_home_left(self, entity, attribute, old, new, kwargs):
        self.log("on_home_left called")
        self.call_service("script/turn_on", entity_id="script.home_left")
