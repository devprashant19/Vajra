from typing import Callable, List, Tuple
from vajra_core.time.clock import Clock
import datetime

class Scheduler:
    def __init__(self, clock: Clock):
        self.clock = clock
        self.tasks: List[Tuple[datetime.datetime, Callable[[], None]]] = []

    def schedule(self, trigger_time: datetime.datetime, task: Callable[[], None]) -> None:
        self.tasks.append((trigger_time, task))
        self.tasks.sort(key=lambda x: x[0])

    def run_pending(self) -> None:
        now = self.clock.now()
        runnable = [t for t in self.tasks if t[0] <= now]
        self.tasks = [t for t in self.tasks if t[0] > now]
        
        for _, task in runnable:
            task()
