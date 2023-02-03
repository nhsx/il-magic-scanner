#!/usr/bin/env python

# Daemon to listen on a socket and start LED patterns based on the character sent on the socket
# Starts up in a "pulsing power LED" mode
# We run at 100 Hz
from math import sin, pi
import os
import asyncio
import time
from pathlib import Path 
from .pca9685 import PCA9685
import toml


class PulsingLight:
    def __init__(self, clock_rate_hz, light_name, pulse_freq=3.0):
        self.t = 0
        self.pulse_freq = pulse_freq
        self.loop_length_s = 1.0/clock_rate_hz
        self.light_name = light_name

    def tick(self):
        """
        tick methods return a {'r': num, 'y': num, 'g': num} dict, in the
        assumption that leaving one out means "no change"
        num is in the range 0-1
        """
        value = (sin(self.t*2*pi*self.pulse_freq)+1.0)/2
        self.t += self.loop_length_s    
        return {self.light_name: value}

class DoublePulse:
    def __init__(self, clock_rate_hz, light_name, pulse_freq=3.0):
        self.t = 0
        self.pulse_freq = pulse_freq
        self.loop_length_s = 1.0/clock_rate_hz
        self.light_name = light_name

    def tick(self):
        freq_multiple =2*pi*self.pulse_freq
        value = (sin(self.t*freq_multiple) + sin(self.t*3*freq_multiple) + 2.0)/4
        self.t += self.loop_length_s    
        if value > 0.5:
            return {self.light_name: value}
        else:
            return {self.light_name: 0}

class SolidLight:
    def __init__(self, light_name, value=1.0):
        self.result = {light_name: value}

    def tick(self):
        return self.result

class PatternMaker:
    def __init__(self, pwm_refresh_rate_hz):
        self.pwm_refresh_rate_hz = pwm_refresh_rate_hz

    def pulsing(self, light_name, pulse_rate_hz):
        return PulsingLight(self.pwm_refresh_rate_hz, light_name, pulse_rate_hz)

    def solid(self, light_name, value=1.0):
        return SolidLight(light_name, value)

    def double_pulse(self, light_name, pulse_rate_hz):
        return DoublePulse(self.pwm_refresh_rate_hz, light_name, pulse_rate_hz)

    def off(self, light_name):
        return self.solid(light_name, 0.0)
    
def collect_patterns(patterns):
    result = {}
    for pattern in patterns:
        result.update(pattern.tick())
    return result

def apply_values(pwm, light_values):
    light_names = ['r', 'y', 'g']
    for i in range(len(light_names)):
        light_name = light_names[i]
        if light_name in light_values:
            pwm.duty(i, int(4095*light_values[light_name]))

async def handle_client(reader, writer):
    global states
    global selected_state
    new_state_name = (await reader.readline()).decode('utf-8').strip()
    if new_state_name in states:
        print("Selecting state", new_state_name)
        selected_state = new_state_name

def listen(socket_path):
    path = Path(socket_path)
    path.parent.mkdir(exist_ok=True, parents=True)
    loop = asyncio.get_event_loop()

    result = loop.run_until_complete(asyncio.start_unix_server(handle_client, path=socket_path))
    os.chmod(socket_path, 0o666)

async def state_loop(pwm):
    global states
    global selected_state

    while True:
        patterns = states[selected_state]
        apply_values(pwm, collect_patterns(patterns))
        await asyncio.sleep(1.0/pwm_refresh_rate_hz)

pwm_refresh_rate_hz = 100
patterns = PatternMaker(pwm_refresh_rate_hz)
states = {
    'start': [patterns.pulsing('r', 0.5), patterns.off('y'), patterns.off('g')],
    'ready': [patterns.solid('r', 1.0), patterns.off('y'), patterns.off('g')],
    'processing': [patterns.pulsing('y', 1.0), patterns.off('g')],
    'success': [patterns.off('y'), patterns.solid('g', 1.0)],
    'alert': [patterns.double_pulse('r', 80.0/60), patterns.off('y'), patterns.off('g')]
}
selected_state = 'start'

if __name__ == "__main__":
    pwm = PCA9685.get()
    pwm.freq(pwm_refresh_rate_hz)

    listen(toml.load("/etc/ledd.conf")['socket_path'])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(state_loop(pwm))
