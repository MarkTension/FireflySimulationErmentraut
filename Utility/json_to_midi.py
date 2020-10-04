"""
This script reads in a JSON file
Parses the keys of interest
Generates a midi file
"""

import json
import numpy as np
from mido import Message, MidiFile, MidiTrack

from collections import OrderedDict

"""
Script interfaces between python and midi bridge (to communicate with ableton Live)

"""


class TimeStepSource(object):
  """
  this object holds the source data for each agent step.
  and
  """
  directionChange = 0
  actionKind = 0

  # The class "constructor" - It's actually an initializer
  def __init__(self, directionChange, actionKind, reward, xyz):
    self.directionChange = directionChange
    self.actionKind = actionKind
    self.reward = reward
    self.xyz = xyz
    self.xyzNorm = np.round((np.array(xyz)/128)*127).astype(int)

  def __repr__(self):
    return f'{self.__class__.__name__}_obj'


def GetActionChanged(input):

  xyzPast = np.zeros(3) # buffer for previous action
  pastDirection = np.zeros(6)

  # [xmin, xmax, ymin, ymax, zmin, zmax]

  for xyz in input:

    xyz = np.array(xyz)

    difference = xyz - xyzPast
    axis = np.argmax(np.abs(difference)) # this is the axis of change
    stepsize = difference[axis]

    maxDirection = stepsize > 0 # this is also the direction of change making e.g. xmin or xmax

    direction = np.zeros(6)
    direction[2*axis + maxDirection] = 1

    directionChanged = not np.array_equal(direction, pastDirection)

    # past is present
    xyzPast = xyz
    pastDirection = direction

    yield directionChanged


def ReadJson():
  """
  reads json file
  :returns dictionary with sources of interest
  """
  # Read first
  with open('1_09_29.json') as json_file:
    data = json.load(json_file)

  # unpack interesting sources
  actionKind = data["AgentPath"]["actionOption"]
  actionXYZ = data["AgentPath"]["xyz"]
  reward = data["AgentData"]["reward_final"]

  length = len(actionXYZ)

  # todo: make front back left right work

  # make directionChange source. These are put into one object
  directionChanged = GetActionChanged(actionXYZ)
  actionKindIter = iter(actionKind)
  reward = iter(reward)
  xyz = iter(actionXYZ)

  soundsource = []

  for i in range(length):
    soundsource.append(TimeStepSource(directionChanged.__next__(),
                                      actionKindIter.__next__(),
                                      reward.__next__(),
                                      xyz.__next__()))

  s = []
  for i in range(length):
    if i % 10 == 0 and i != 0:
      s.append(soundsource[i])

  return s

def GenerateMidiFile(source, name):

  timestep = 3 # there are three ticks per beat in general

  mid = MidiFile()
  mid.type = 2
  track = MidiTrack()
  track.name = "actions"
  track_panning = MidiTrack()
  track_panning.name = "panning"
  track_depth = MidiTrack()
  track_depth.name = "depth"
  mid.tracks.append(track)
  mid.tracks.append(track_panning)
  mid.tracks.append(track_depth)

  track.append(Message('program_change', program=12, time=timestep))
  track_panning.append(Message('program_change', program=12, time=timestep))
  track_depth.append(Message('program_change', program=12, time=timestep))

  for event in source:

    velocity = np.round(event.reward * 10).astype(int) # max is ~ .6, so we have 6 levels of velocity to play with

    # two simultaneous notes
    # if event.directionChange:
    #   track.append(Message('note_on', note=64, velocity=64, time=timestep))
    #   track.append(Message('note_off', note=64, velocity=64, time=timestep))

    track.append(Message('note_on', note=65 + int(event.actionKind), velocity=64 + velocity, time=timestep))
    track.append(Message('note_off', note=65 + int(event.actionKind), velocity=64 + velocity, time=timestep))

    track_panning.append(Message('note_on', note=0 , velocity=0 + event.xyzNorm[0],  time=timestep))
    track_panning.append(Message('note_off', note=0 , velocity=0 + event.xyzNorm[0],  time=timestep))

    track_depth.append(Message('note_on', note=0, velocity= 0 + event.xyzNorm[2],  time=timestep))
    track_depth.append(Message('note_off', note=0, velocity= 0 + event.xyzNorm[2],  time=timestep))

  mid.save(f'{name}s.mid')


# main script starts here
name = "agent105_10_2_includingdepthPan"

soundSources = ReadJson()
# encode sounds into midi
GenerateMidiFile(soundSources, name=name)

