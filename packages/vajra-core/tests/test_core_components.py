import pytest
import datetime
from vajra_core.time.clock import RealClock, ReplayClock
from vajra_core.registry.variables import REGISTRY, celsius_to_kelvin

def test_clocks():
    rc = RealClock()
    assert isinstance(rc.now(), datetime.datetime)
    
    start_time = datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    sc = ReplayClock(start_time=start_time, speed=1.0)
    assert abs((sc.now() - start_time).total_seconds()) < 0.1
    
    sc.advance(60)
    assert abs((sc.now() - (start_time + datetime.timedelta(seconds=60))).total_seconds()) < 0.1

def test_registry():
    var = REGISTRY["reflectivity"]
    assert var.name == "reflectivity"
    assert var.unit == "dBZ"
    assert celsius_to_kelvin(0.0) == 273.15
    
def test_logger():
    import logging
    from vajra_core.logging.logger import setup_logging
    setup_logging()
    log = logging.getLogger("test_log")
    log.info("Test message")

def test_scheduler():
    from vajra_core.time.scheduler import Scheduler
    from vajra_core.time.clock import RealClock
    
    rc = RealClock()
    s = Scheduler(rc)
    events = []
    
    def my_job():
        events.append(1)
        
    s.schedule(rc.now() + datetime.timedelta(seconds=0.1), my_job)
    s.run_pending()
    assert len(events) == 0
    
    import time
    time.sleep(0.15)
    s.run_pending()
    assert len(events) == 1
