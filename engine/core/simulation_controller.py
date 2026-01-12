from __future__ import annotations


class SimulationController:
    """
    Controls execution state of the simulation.

    Does not know about input, rendering, or physics internals.
    """

    __slots__ = ("paused", "_step_requested", "_reset_requested")

    def __init__(self) -> None:
        self.paused: bool = False
        self._step_requested: bool = False
        self._reset_requested: bool = False

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def request_step(self) -> None:
        if self.paused:
            self._step_requested = True

    def request_reset(self) -> None:
        self.paused = True
        self._reset_requested = True

    def should_step(self) -> bool:
        """
        Returns True if the simulation should advance this frame.
        """
        if not self.paused:
            return True

        if self._step_requested:
            self._step_requested = False
            return True

        return False

    def should_reset(self) -> bool:
        """
        Returns True if a reset was requested.
        """
        if self._reset_requested:
            self._reset_requested = False
            return True
        return False
