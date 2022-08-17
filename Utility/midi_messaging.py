import mido
import json

"""
Script interfaces between python and midi bridge (to communicate with ableton Live)

"""
agents = None
pitch = 0

import mido
# from main import Params

pitch = 0

# callback to receive MIDI messages
def print_message(message):
  print(message)
  for agent in agents:
    agent.reset_sync()


# # midi input port and output port
# mido.get_output_names()
# outport = mido.open_output('MidiBridge1', virtual=True)
# inport = mido.open_input("MidiBridge2", callback=print_message)

# message output function
def Send(note, id, velocity):
  # print('commented out')
  a = 0
  # outport.send(mido.Message('note_on', note=50 + id + pitch, velocity=64))



