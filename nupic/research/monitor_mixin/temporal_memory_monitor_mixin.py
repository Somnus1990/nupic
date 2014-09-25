# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2014, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
Temporal Memory mixin that enables detailed monitoring of history.
"""

from nupic.research.monitor_mixin.trace import (
  IndicesTrace, BoolsTrace, StringsTrace)
from nupic.research.monitor_mixin.monitor_mixin_base import MonitorMixinBase


class TemporalMemoryMonitorMixin(MonitorMixinBase):
  """
  Mixin for TemporalMemory that stores a detailed history, for inspection and
  debugging.
  """

  def __init__(self, *args, **kwargs):
    super(TemporalMemoryMonitorMixin, self).__init__(*args, **kwargs)

    self._traces["activeColumns"] = IndicesTrace("active columns")
    self._traces["predictiveCells"] = IndicesTrace("predictive cells")
    self._traces["sequenceLabels"] = StringsTrace("sequence labels")
    self._traces["resets"] = BoolsTrace("resets")

    self._transitionTracesComputed = False


  def getTraceActiveColumns(self):
    """
    @return (Trace) Trace of active columns
    """
    return self._traces["activeColumns"]


  def getTracePredictiveCells(self):
    """
    @return (Trace) Trace of predictive cells
    """
    return self._traces["predictiveCells"]


  def getTraceSequenceLabels(self):
    """
    @return (Trace) Trace of sequence labels
    """
    return self._traces["sequenceLabels"]


  def getTraceResets(self):
    """
    @return (Trace) Trace of resets
    """
    return self._traces["resets"]


  def getTracePredictedActiveCells(self):
    """
    @return (Trace) Trace of predicted => active cells
    """
    self._computeTransitionTraces()
    return self._traces["predictedActiveCells"]


  def getTracePredictedInactiveCells(self):
    """
    @return (Trace) Trace of predicted => inactive cells
    """
    self._computeTransitionTraces()
    return self._traces["predictedInactiveCells"]


  def getTracePredictedActiveColumns(self):
    """
    @return (Trace) Trace of predicted => active columns
    """
    self._computeTransitionTraces()
    return self._traces["predictedActiveColumns"]


  def getTracePredictedInactiveColumns(self):
    """
    @return (Trace) Trace of predicted => inactive columns
    """
    self._computeTransitionTraces()
    return self._traces["predictedInactiveColumns"]


  def getTraceUnpredictedActiveColumns(self):
    """
    @return (Trace) Trace of unpredicted => active columns
    """
    self._computeTransitionTraces()
    return self._traces["unpredictedActiveColumns"]


  def _computeTransitionTraces(self):
    """
    Computes the transition traces, if necessary.

    Transition traces are the following:

        predicted => active cells
        predicted => inactive cells
        predicted => active columns
        predicted => inactive columns
        unpredicted => active columns
    """
    if self._transitionTracesComputed:
      return

    self._traces["predictedActiveCells"] = IndicesTrace(
      "predicted => active cells")
    self._traces["predictedInactiveCells"] = IndicesTrace(
      "predicted => inactive cells")
    self._traces["predictedActiveColumns"] = IndicesTrace(
      "predicted => active columns")
    self._traces["predictedInactiveColumns"] = IndicesTrace(
      "predicted => inactive columns")
    self._traces["unpredictedActiveColumns"] = IndicesTrace(
      "unpredicted => active columns")

    predictiveCellsTrace = self.getTracePredictiveCells()
    prevPredictiveCells = set()

    for i, activeColumns in enumerate(self.getTraceActiveColumns().data):
      predictedActiveCells = set()
      predictedInactiveCells = set()
      predictedActiveColumns = set()
      predictedInactiveColumns = set()

      for prevPredictedCell in prevPredictiveCells:
        prevPredictedColumn = self.connections.columnForCell(prevPredictedCell)

        if prevPredictedColumn in activeColumns:
          predictedActiveCells.add(prevPredictedCell)
          predictedActiveColumns.add(prevPredictedColumn)
        else:
          predictedInactiveCells.add(prevPredictedCell)
          predictedInactiveColumns.add(prevPredictedColumn)

      unpredictedActiveColumns = activeColumns - predictedActiveColumns

      self._traces["predictedActiveCells"].data.append(predictedActiveCells)
      self._traces["predictedInactiveCells"].data.append(predictedInactiveCells)
      self._traces["predictedActiveColumns"].data.append(predictedActiveColumns)
      self._traces["predictedInactiveColumns"].data.append(
        predictedInactiveColumns)
      self._traces["unpredictedActiveColumns"].data.append(
        unpredictedActiveColumns)

      prevPredictiveCells = predictiveCellsTrace.data[i]

    self._transitionTracesComputed = True


  def _clearTransitionTraces(self):
    """
    Clears the transition traces. (See `_computeTransitionTraces` for more
    information.)
    """
    self._traces["predictedActiveCells"] = None

    self._transitionTracesComputed = False


  # ==============================
  # Overrides
  # ==============================

  def compute(self, activeColumns, sequenceLabel=None, **kwargs):
    super(TemporalMemoryMonitorMixin, self).compute(activeColumns, **kwargs)

    self._traces["predictiveCells"].data.append(self.predictiveCells)
    self._traces["activeColumns"].data.append(activeColumns)
    self._traces["sequenceLabels"].data.append(sequenceLabel)

    resetsTrace = self._traces["resets"]
    # First iteration is always a reset
    reset = False if len(resetsTrace.data) else True
    self._traces["resets"].data.append(reset)

    self._clearTransitionTraces()


  def reset(self):
    super(TemporalMemoryMonitorMixin, self).reset()

    self._traces["resets"].data[-1] = True

    self._clearTransitionTraces()

