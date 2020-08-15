import numpy as np
import random
import time

class Agent():
  def __init__(self, id, params):
    self.time = 0
    self.id = id
    self.params = params
    self.omegaCommon = params.NaturalFrequency # natural frequency shared amongst all agents
    self.time_cur = 0
    self.OmegaHigh = params.OmegaHigh # high bound frequency
    self.OmegaLow = params.OmegaLow # low bound frequency
    self.omegaCurrent = random.uniform(self.OmegaLow, self.OmegaHigh) # cycle length, bound by deltaLow and deltaHigh
    self.delta = 1 / self.omegaCurrent
    self.phi = 0  # the phase [0 to 1]
    self.epsilon = params.epsilon  # controls the tendency of the frequency to move towards
    self.latestFlashProcessed = -1 # shouldn't be zero
    self.timestep = 1 /params.fps # size of step in time

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


