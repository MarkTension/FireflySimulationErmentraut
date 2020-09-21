import numpy as np
import time
import plotly.graph_objects as go
import agentConstructor
import connectivity  # imports the overlay network for graph connections of fireflies

"""
This is a simulation for firefly synchronisation
Ermentraut algorithm and general algorothm are largely based on Firefly-inspired Heartbeat Synchronization in Overlay Networks, 
http://www.cs.unibo.it/babaoglu/courses/cas06-07/papers/pdf/fireflies.pdf . 
Adapted for discrete time simulation

Kuramoto implementation is based on Strogatz's excellent review on the kuramoto model
https://www.seas.upenn.edu/~jadbabai/ESE680/Strogatz_Kuramoto.pdf
"""

class params:
  """
  parameters for simulation
  """
  algorithm = ["ermentraut","mirollo-strogatz"][1]  # firefly algorithm. Choose: index
  fps = 90                                          # frames per second (simulation speed)
  numAgents = 800                                   # 800 works well
  NaturalFrequency = 0.5                            # natural frequency of an agent
  OmegaHigh = 1                                     # upper bound frequency
  OmegaLow = 0.3                                    # lower bound frequency
  numNeighbors = 30                                 # how many neighbors for each agent
  epsilon = 0.01                                    # tendency for the agent to move to natural frequecy
  pitch  = 0
  reduce_frequency = False                          # does the main loop reduce the natural frequency every n steps?

# np.random.seed(420)

# generate adjacency matrix for connectivity
adjMatrix = connectivity.BuildGraph(params)

# initialize agents
agents = []
for i in range(params.numAgents):
  if (params.algorithm == "ermentraut"):
    agents.append(agentConstructor.ErmentrautAgent(i, params))
  elif (params.algorithm == "mirollo-strogatz"):
    agents.append(agentConstructor.MirolloStrogatz(i, params))
  else:
    raise ValueError(f"{params.algorithm} does not exist")


# initialize midi interface
import midiUtils    # imports midi i/o
midiUtils.agents = agents

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

# quite arbitrary: which firefly id's go to midi?
fireFlies = [31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]

while running:
    lastFrameTime = StepTime(lastFrameTime) # makes loop controlable in time
    flashes = [] # will contain id's of agents that fired

    # increase each agent's phase
    # and check if phase is 1. If so, flash
    for agent in agents:
      agent.omegaCommon = params.NaturalFrequency  # this is only for changing the frequency
      flashoutID = agent.CheckTime()
      if (flashoutID != False):
        flashes.append(flashoutID)  # returns ID of fireflies with phase > 1

        if (flashoutID in fireFlies):
          midiUtils.Send(note=50+flashoutID, id=flashoutID, velocity=64)

        # save for figure
        PlotTimestamp.append(counter/params.fps)
        PlotAgent.append(flashoutID)

    if (params.reduce_frequency and counter % 3000 == 0 and counter/params.fps != 0):
      params.NaturalFrequency *= 0.75
      print(f"natural freq lowererd to {params.NaturalFrequency}")

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
    if (counter % (params.fps*10) == 0 and counter > 0):
      adjMatrix = connectivity.BuildGraph(params)
      print(f"new graph{counter}")

    counter+=1