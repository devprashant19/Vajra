import datetime
from abc import ABC, abstractmethod
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = datetime.timezone.utc

class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime.datetime:
        """Return the current time in UTC."""
        pass
    
    def now_ist(self) -> datetime.datetime:
        """Return the current time in IST (for display/logging)."""
        return self.now().astimezone(IST)

class RealClock(Clock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(tz=UTC)

class ReplayClock(Clock):
    def __init__(self, start_time: datetime.datetime, speed: float = 1.0):
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=UTC)
        self._current_time = start_time
        self._speed = speed
        self._real_start = datetime.datetime.now(tz=UTC)
    
    def now(self) -> datetime.datetime:
        """Calculates current replay time based on elapsed real time and speed factor."""
        elapsed_real = (datetime.datetime.now(tz=UTC) - self._real_start).total_seconds()
        elapsed_replay = elapsed_real * self._speed
        return self._current_time + datetime.timedelta(seconds=elapsed_replay)
    
    def set_time(self, new_time: datetime.datetime) -> None:
        if new_time.tzinfo is None:
            new_time = new_time.replace(tzinfo=UTC)
        self._current_time = new_time
        self._real_start = datetime.datetime.now(tz=UTC)
        
    def advance(self, seconds: float) -> None:
        self._current_time += datetime.timedelta(seconds=seconds)
        self._real_start = datetime.datetime.now(tz=UTC)

    def set_speed(self, speed: float) -> None:
        # Before changing speed, lock in the current simulated time
        current = self.now()
        self._speed = speed
        self._current_time = current
        self._real_start = datetime.datetime.now(tz=UTC)
