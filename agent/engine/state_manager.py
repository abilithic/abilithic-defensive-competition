"""Agent State Manager (TDD §8.2, §35).

State agent: INIT -> REGISTERED -> WAITING -> RUNNING <-> PAUSED -> ENDED
(+ OFFLINE saat kehilangan koneksi). Transisi dipicu STATUS dari server
(server = sumber kebenaran tunggal).
"""
from enum import Enum


class AgentState(str, Enum):
    INIT = "init"
    REGISTERED = "registered"
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    OFFLINE = "offline"
    ENDED = "ended"


# Pemetaan status server -> state agent
_SERVER_TO_STATE = {
    "waiting": AgentState.WAITING,
    "running": AgentState.RUNNING,
    "paused": AgentState.PAUSED,
    "ended": AgentState.ENDED,
    "archived": AgentState.ENDED,
}


class StateManager:
    def __init__(self, logger):
        self.state = AgentState.INIT
        self.log = logger
        self._start_captured = False
        self._stop_captured = False

    def mark_registered(self):
        if self.state == AgentState.INIT:
            self._set(AgentState.REGISTERED)

    def mark_offline(self):
        # hanya tandai offline bila sedang aktif (jangan timpa ENDED)
        if self.state in (AgentState.RUNNING, AgentState.WAITING, AgentState.PAUSED):
            self._prev_before_offline = self.state
            self._set(AgentState.OFFLINE)

    def apply_server_status(self, server_status: str):
        """Terapkan status dari server. Return state baru."""
        target = _SERVER_TO_STATE.get(server_status)
        if target is None:
            return self.state
        # Jangan mundur dari ENDED
        if self.state == AgentState.ENDED:
            return self.state
        if target != self.state:
            self._set(target)
        return self.state

    # --- flag pengambilan snapshot (sekali saja) ---
    def should_capture_start(self) -> bool:
        if self.state == AgentState.RUNNING and not self._start_captured:
            self._start_captured = True
            return True
        return False

    def should_capture_stop(self) -> bool:
        if self.state == AgentState.ENDED and not self._stop_captured:
            self._stop_captured = True
            return True
        return False

    def is_scoring(self) -> bool:
        return self.state == AgentState.RUNNING

    def _set(self, new_state: AgentState):
        old = self.state
        self.state = new_state
        self.log.info("state_transition", **{"from": old.value, "to": new_state.value})
