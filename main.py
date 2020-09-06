import numpy as np
import time
from agentClass import Agent
import connectivity

import plotly.express as px
import plotly.graph_objects as go
from synthesizer import Player, Synthesizer, Waveform

import mido

outport = mido.open_output('MidiBridge1')


"""
This is a simulation for firefly synchronisation
Based on Firefly-inspired Heartbeat Synchronization in Overlay Networks, 
http://www.cs.unibo.it/babaoglu/courses/cas06-07/papers/pdf/fireflies.pdf

Adapted for discrete time simulation
"""

class params:
  """
  parameters for simulation
  """
  fps = 260                 # frames per second (simulation speed)
  numAgents = 800          # 800 works well
  NaturalFrequency = 1    # natural frequency of an agent
  OmegaHigh = 1.5         # upper bound frequency
  OmegaLow = 0.3          # lower bound frequency
  connectivity = 0.2      # how densely connected: [0 - 1] 0.1 for 800
  epsilon = 0.01          # tendency for the agent to move to natural frequecy

np.random.seed(420)
player = Player()
player.open_stream()
synthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=1.0, use_osc2=False)

# generate adjacency matrix for connectivity
adjMatrix = connectivity.BuildGraph(params.numAgents, params.connectivity, 0)

# initialize agents
agents = []
for i in range(params.numAgents):
  agents.append(Agent(i, params))


# step time in intervals
def StepTime(lastFrameTime):
  currentTime = time.time()
  sleepTime = 1. / params.fps - (currentTime - lastFrameTime)
  if sleepTime > 0:
    time.sleep(sleepTime)
  else:
    lastFrameTime = time.time()

  return lastFrameTime


"""
environment
"""
# make time loop for discrete timesteps
running = True
lastFrameTime = time.time()
# empty numpy array for environmental state
soundState = np.empty(params.numAgents)
ids = np.arange(0, params.numAgents)
startTime = time.time()
TimeZero = time.time()

PlotTimestamp = []
PlotAgent = []

counter = 0

fireFlies = [31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

while running:
    lastFrameTime = StepTime(lastFrameTime) # makes loop controlable in time
    flashes = [] # will contain id's of agents that fired

    # loop through agents at timepoint.
    # and check if phase is 1. If so, flash
    for agent in agents:
      agent.omegaCommon = params.NaturalFrequency
      flashoutID = agent.CheckTime()
      if (flashoutID != False):
        flashes.append(flashoutID) # returns ID of flashmaker

        if (flashoutID in fireFlies):
          # player.play_wave(synthesizer.generate_constant_wave(80.0 * (flashoutID/10), 0.1))
          outport.send(mido.Message('note_on', note=50+flashoutID, velocity=64))

        # save for figure
        PlotTimestamp.append(counter/params.fps)
        PlotAgent.append(flashoutID)

    # if (counter % 3000 == 0 and counter/params.fps != 0):
    #   params.NaturalFrequency *= 0.75
    #   print(f"natural freq lowererd to {params.NaturalFrequency}")

    # send flashes to connected neighbors
    if (len(flashes) > 0):
      for source in flashes:
        neighbors = adjMatrix[source]
        # send flash
        for neighbor in neighbors:
          agents[neighbor].ProcessFlash()


    # PLOT DATA
    if (counter % 1900 == 0 and counter > 0):
      fig = go.Figure(data=go.Scatter(x=PlotTimestamp, y=PlotAgent, mode='markers', marker=dict(size=3, color="Blue", opacity=0.6)))
      fig.show()

    # generate new graph for random connectivity
    if (counter % params.fps*10 == 0 and counter > 0):
      adjMatrix = connectivity.BuildGraph(params.numAgents, params.connectivity, counter)

    counter+=1