import mido

"""
Script interfaces between python and midi bridge (to communicate with ableton Live)

"""
agents = None
pitch = 0

import mido
# from main import params

pitch = 0

# callback to receive MIDI messages
def print_message(message):
  print(message)
  for agent in agents:
    agent.ResetSync()
  # outport.send(message)
  # params.pitch += 20


# midi input port and output port
outport = mido.open_output('MidiBridge1')
inport = mido.open_input("MidiBridge2", callback=print_message)

# message output function
def Send(note, id, velocity):
  outport.send(mido.Message('note_on', note=50 + id + pitch, velocity=64))

