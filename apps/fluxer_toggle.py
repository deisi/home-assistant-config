
"""App to toggle the fluxer depending on the state of all its members.

A problem of the fluxer is, that it tends to reactivate lights, after they
have been turned off by hand. This app checks if all lights that are monitored
by the fluxer are on, and if so, the fluxer is turned on.
If a single member of the fluxer is turned off, then this app tuns off the
fluxer."""

import appdaemon.appapi as appapi
from time import sleep

# List of lights that are members of the fluxer
# TODO findout how to read this from HA itself.
lights = [
    'light.beamer',
    'light.sofa0',
    'light.sofa1',
    'light.kueche0',
    'light.kueche1',
    'light.tisch0',
    'light.tisch1',
    'light.ofen0',
    'light.ofen1',
    'light.schnapsschrank0',
    'light.schnapsschrank1',
    'light.kueche2',
    'light.kuche',
    'light.bunt',
    'light.esszimmer',
    'light.lightify',
    'light.ofen',
    'light.wohnzimmer'
]


class ToggleFluxer(appapi.AppDaemon):

    def initialize(self):
        self.listen_event(self.toggle_fluxer, 'state_changed')

    def fluxer_off(self):
        self.turn_off('switch.fluxer')

    def fluxer_on(self):
        self.turn_on('switch.fluxer')

    @property
    def all_lights_on(self):
        if all([self.get_state(light) for light in lights]):
            return True
        return False

    def toggle_fluxer(self, event_name, data, kwargs):
        if data['entity_id'] not in lights:
            return

        #if data['new_state']['attributes'].get('rgb_color') != data['old_state']['attributes'].get('rgb_color'):
        #    self.fluxer_off()
        #    print('Turned fluxer off due to color change.')
        #    return

        if data['new_state']['state'] == data['old_state']['state']:
            return

        if data['new_state']['state'] == 'off':
            self.fluxer_off()
            print('Turned fluxer off')
            return

        # Lightify needs some time to settle
        sleep(1)
        if self.all_lights_on:
            self.fluxer_on()
            print('Turned fluxer on')
            return
        print('Called but noting was cahnged. Data is:', data)
