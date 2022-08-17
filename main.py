import numpy as np
import time
import plotly.graph_objects as go
import agentConstructor

from utility import midi_messaging, connectivity

"""
This is a simulation for firefly synchronisation
Ermentraut algorithm and general algorothm are largely based on Firefly-inspired Heartbeat Synchronization in Overlay Networks, 
http://www.cs.unibo.it/babaoglu/courses/cas06-07/papers/pdf/fireflies.pdf . 
Adapted for discrete time simulation

Kuramoto implementation is based on Strogatz's excellent review on the kuramoto model
https://www.seas.upenn.edu/~jadbabai/ESE680/Strogatz_Kuramoto.pdf
"""

class Params:
  """
  parameters for simulation
  """
  algorithm = ["ermentraut", "mirollo-strogatz"][0]  # firefly algorithm. Choose: index
  fps = 90  # frames per second (simulation speed)
  num_agents = 800  # 800 works well
  natural_frequency = 1  # natural frequency of an agent
  omega_high = 1.5  # upper bound frequency
  omega_low = 0.8  # lower bound frequency
  num_neighbors = 30  # how many neighbors for each agent # 30 often converges
  epsilon = 0.01  # tendency for the agent to move to natural frequecy
  pitch = 0
  reduce_frequency = False  # does the main loop reduce the natural frequency every n steps?
  visualize = True


# np.random.seed(420)

# generate adjacency matrix for connectivity
adj_matrix = connectivity.build_graph(Params)

# initialize agents
agents = []
for i in range(Params.num_agents):
  if (Params.algorithm == "ermentraut"):
    agents.append(agentConstructor.ErmentrautAgent(i, Params))
  elif (Params.algorithm == "mirollo-strogatz"):
    agents.append(agentConstructor.MirolloStrogatz(i, Params))
  else:
    raise ValueError(f"{Params.algorithm} does not exist")

# for midi sending to ableton
midi_messaging.agents = agents


# step time in intervals
def StepTime(last_frame_time):
  currentTime = time.time()
  sleepTime = 1. / Params.fps - (currentTime - last_frame_time)
  if sleepTime > 0:
    time.sleep(sleepTime)
  else:
    last_frame_time = time.time()

  return last_frame_time


"""
environment
"""
# make time loop for discrete timesteps
running = True
last_frame_time = time.time()
# empty numpy array for environmental state
ids = np.arange(0, Params.num_agents)

plot_time_stamp = []
plot_agent = []
counter = 0

# quite arbitrary: which firefly id's go to midi?
fireflies = [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]

while running:
  last_frame_time = StepTime(last_frame_time)  # makes loop controlable in time
  flashes = []  # will contain id's of agents that fired

  # increase each agent's phase
  # and check if phase is 1. If so, flash
  for agent in agents:
    agent.omegaCommon = Params.natural_frequency  # this is only for changing the frequency
    flashout_id = agent.check_time()
    if (flashout_id != False):
      flashes.append(flashout_id)  # returns ID of fireflies with phase > 1

      if (flashout_id in fireflies):
        midi_messaging.Send(note=50 + flashout_id, id=flashout_id, velocity=64)

      # save for figure
      plot_time_stamp.append(counter / Params.fps)
      plot_agent.append(flashout_id)

  if (Params.reduce_frequency and counter % 3000 == 0 and counter / Params.fps != 0):
    Params.natural_frequency *= 0.75
    print(f"natural freq lowererd to {Params.natural_frequency}")

  # send flashes to connected neighbors
  if (len(flashes) > 0):
    for source in flashes:
      neighbors = adj_matrix[source]
      # send flash
      for neighbor in neighbors:
        agents[neighbor].process_flash()

  # PLOT DATA
  if (counter % 1900 == 0 and counter > 0 and Params.visualize):
    fig = go.Figure(data=go.Scatter(x=plot_time_stamp, y=plot_agent, mode='markers',
                                    marker=dict(size=4.5, color="Blue", opacity=0.6)))
    fig.show()

  # generate new graph for random connectivity
  if (counter % (Params.fps * 10) == 0 and counter > 0):
    adj_matrix = connectivity.build_graph(Params)
    print(f"new graph{counter}")

  counter += 1
