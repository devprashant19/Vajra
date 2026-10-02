import datetime
from vajra_core.time.clock import ReplayClock, UTC
import time

def test_replay_clock_operations():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    start = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    clock = ReplayClock(start_time=start, speed=1.0)
    
    # Check set_time
    new_time = datetime.datetime(2023, 1, 2, 12, 0, 0, tzinfo=UTC)
    clock.set_time(new_time)
    assert abs((clock.now() - new_time).total_seconds()) < 0.1
    
    # Check advance
    clock.advance(3600.0) # advance 1 hour
    expected = new_time + datetime.timedelta(seconds=3600)
    assert abs((clock.now() - expected).total_seconds()) < 0.1
    
    # Check speed change (run at 10x)
    clock.set_speed(10.0)
    t1 = clock.now()
    time.sleep(0.1) # sleep 100ms real time
    t2 = clock.now()
    
    elapsed_replay = (t2 - t1).total_seconds()
    # 100ms real time at 10x speed = 1.0s replay time
    assert 0.8 < elapsed_replay < 1.5
