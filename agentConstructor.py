import numpy as np
import random
import time

class Agent():
  def __init__(self, id, params):
    self.time = 0
    self.id = id
    self.params = params
    self.omegaCommon = params.NaturalFrequency # natural frequency shared amongst all agents
    self.OmegaHigh = params.OmegaHigh # high bound frequency
    self.OmegaLow = params.OmegaLow # low bound frequency
    self.omegaCurrent = random.uniform(self.OmegaLow, self.OmegaHigh) # cycle length, bound by deltaLow and deltaHigh
    self.delta = 1 / self.omegaCurrent
    self.time_cur = random.uniform(0, self.delta)
    self.phi = random.uniform(0, 1)  # the phase [0 to 1]
    self.epsilon = params.epsilon  # controls the tendency of the frequency to move towards
    self.latestFlashProcessed = -1 # shouldn't be zero
    self.timestep = 1 /params.fps # size of step in time
    self.numResets = 0


  def ResetSync(self):
    self.omegaCurrent = random.uniform(self.OmegaLow, self.OmegaHigh)
    self.numResets+=1


  def ProcessFlash(self):
    """
    processes incoming flash
    """
    return NotImplementedError


  def CheckTime(self):
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
  def __init__(self, id, params):
    super().__init__(id, params)

  def ProcessFlash(self):
    """
    processes incoming flash
    """
    #  make sure only one flash is received per timestep
    # if (np.isclose(self.latestFlashProcessed, self.time_cur, rtol=1e-05, atol=1e-08, equal_nan=False)):
    #   pass # already processed a flash this timestep
    # else:
    self.latestFlashProcessed = self.time_cur
    gPlus = np.max((np.sin(2 * np.pi * self.phi) / (2 * np.pi), 0))
    gMin = -np.min((np.sin(2 * np.pi * self.phi) / (2 * np.pi), 0))

    self.omegaCurrent = self.omegaCurrent + self.epsilon * (self.omegaCommon - self.omegaCurrent) \
                        + gPlus * self.phi * (self.OmegaLow - self.omegaCurrent) \
                        + gMin * self.phi * (self.OmegaLow - self.omegaCurrent)

    # adapt self.delta
    self.delta = 1 / self.omegaCurrent



class MirolloStrogatz(Agent):
  """
  Mirollo-Strogatz is a model working with phase manipulations
  These manipulations go through a non-linear "Voltage" function
  """
  def __init__(self, id, params):
    super().__init__(id, params)
    self.voltage = 0
    self.omegaCurrent = self.omegaCommon  # overwrite th variable distribution
    self.phi = 0 #todo: fix this

  def ProcessFlash(self):
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

