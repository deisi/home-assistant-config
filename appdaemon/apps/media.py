"""App to control media related settings"""

import appdaemon.plugins.hass.hassapi as hass

class Media(hass.Hass):

    def initialize(self):
        # Formaly tv beats radio
        self.listen_state(self.turn_off_radio, "media_player.kodi_serv", new="playing")

    def turn_off_radio(self, entity, attribute, old, new, kwargs):
        self.call_service(
            'media_player/media_pause',
            entity_id='media_player.mpd',
        )
        # check if local spotify player is playing
        self.call_service(
            'media_player/media_pause',
            entity_id='media_player.spotify'
        )
        #self.turn_on_denon('CD')

    def turn_on_denon(self, source=None, volume_level=None, delay=4):
        """Function to turn on denon, switch to selected source and set volume."""
        self.turn_on("media_player.denon")
        if source:
            self.call_service(
                'media_player/select_source',
                entity_id='media_player.denon',
                source=source,
                )
        if volume_level:
            self.run_in(
                lambda x: self.call_service(
                    'media_player/volume_set',
                    entity_id='media_player.denon',
                    volume_level=volume_level,
                ),
                delay,
            )
