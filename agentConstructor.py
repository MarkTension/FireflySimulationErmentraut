import numpy as np
import random
import time

class Agent():
  def __init__(self, id, Params):
    self.time = 0
    self.id = id
    self.Params = Params
    self.omega_common = Params.natural_frequency # natural frequency shared amongst all agents
    self.omega_high = Params.omega_high # high bound frequency
    self.omega_low = Params.omega_low # low bound frequency
    self.omega_current = random.uniform(self.omega_low, self.omega_high) # cycle length, bound by deltaLow and deltaHigh
    self.delta = 1 / self.omega_current
    self.time_cur = random.uniform(0, self.delta)
    self.phi = random.uniform(0, 1)  # the phase [0 to 1]
    self.epsilon = Params.epsilon  # controls the tendency of the frequency to move towards
    self.timestep = 1 /Params.fps # size of step in time
    self.num_resets = 0


  def reset_sync(self):
    # print(f"{self.id} has reset from {self.time_cur}")
    self.omega_current = random.uniform(self.omega_low, self.omega_high)
    self.time_cur = random.uniform(0, self.delta)
    self.num_resets+=1


  def process_flash(self):
    """
    processes incoming flash
    """
    return NotImplementedError


  def check_time(self):
      """
      advances time, and checks if phase at end of cycle time
      """
      self.time_cur += self.timestep  # increase time according to fps

      self.phi = self.time_cur / self.delta  # adjust phi

      if (self.time_cur >= self.delta):
        self.time_cur = 0

        return self.id # flash

      else:
        return False # don't flash


class ErmentrautAgent(Agent):
  """
    Ermentraut is a model working with cycle-length manipulations
  """
  def __init__(self, id, Params):
    super().__init__(id, Params)

  def process_flash(self):
    """
    processes incoming flash
    """
   
    gPlus = np.max((np.sin(2 * np.pi * self.phi) / (2 * np.pi), 0))
    gMin = -np.min((np.sin(2 * np.pi * self.phi) / (2 * np.pi), 0))

    self.omega_current = self.omega_current + self.epsilon * (self.omega_common - self.omega_current) \
                        + gPlus * self.phi * (self.omega_low - self.omega_current) \
                        + gMin * self.phi * (self.omega_low - self.omega_current)

    # adapt self.delta
    self.delta = 1 / self.omega_current



class MirolloStrogatz(Agent):
  """
  Mirollo-Strogatz is a model working with phase manipulations
  These manipulations go through a non-linear "Voltage" function
  """
  def __init__(self, id, Params):
    super().__init__(id, Params)
    self.voltage = 0
    self.omega_current = self.omega_common  # overwrite th variable distribution
    self.phi = 0 #todo: fix this
    raise NotImplementedError("This agent is not implemented. Please use Ermentraut")

  def process_flash(self):
    """
    processes incoming flash
    """

    # x = f(φ)
    # voltage adjustment: x′ =min(x + ε, 1)
    # phase adjustment  : φ′ = f−1(x′)

    # intuition: every flash it gets, voltage is increased.
    # self.voltage = np.min(self.voltage + self.epsilon, 1)
    # self.phi = self.voltage

    # adapt self.delta
    self.phi = 0

