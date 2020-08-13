import numpy as np
import time
from agentClass import Agent
import connectivity

import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go

import matplotlib.pyplot as plt



class params:
  fps = 60
  numAgents = 800
  NaturalFrequency = 1 # Hz 
  OmegaHigh = 1.5
  OmegaLow = 0.5
  connectivity = 0.1
  epsilon = 0.01

np.random.seed(420)

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

while running:
    lastFrameTime = StepTime(lastFrameTime) # makes loop controlable in time
    flashes = [] # will contain id's of agents that fired

    # loop through agents at timepoint.
    # and check if phase is 1. If so, flash
    for agent in agents:
      flashoutID = agent.CheckTime()
      if (flashoutID != False):
        flashes.append(flashoutID) # returns ID of flashmaker

        # save for figure
        PlotTimestamp.append(counter/params.fps)
        PlotAgent.append(flashoutID)

    # send flashes to connected neighbors
    if (len(flashes) > 0):
      for source in flashes:
        neighbors = adjMatrix[source]
        # send flash
        for neighbor in neighbors:
          agents[neighbor].ProcessFlash()


    # PLOT DATA
    if (counter % 600 == 0 and counter > 0):
      fig = go.Figure(data=go.Scatter(x=PlotTimestamp, y=PlotAgent, mode='markers', marker=dict(size=3, color="Blue", opacity=0.6)))
      fig.show()

    # generate new graph for random connectivity
    if (counter % params.fps*10 == 0 and counter > 0):
      adjMatrix = connectivity.BuildGraph(params.numAgents, params.connectivity, counter)

    counter+=1