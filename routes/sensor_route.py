from fastapi import APIRouter
from sniffio import current_async_library
from models.data_sensor_model import Datasensor
from schemas.data_sensor_schemas import Data_Sensor_Entity , Datas_Sensors_Entity
from config.db import connect
import datetime
import time
import random

from threading import Thread, Event
from typing import Callable

sensor = APIRouter()
Path = connect.WASTETREATMENT.data_sensor

class TimedCalls(Thread):
    """Call function again every `interval` time duration after it's first run."""
    def __init__(self, func: Callable, interval: datetime.timedelta) -> None:
        super().__init__()
        self.func = func
        self.interval = interval
        self.stopped = Event()

    def cancel(self):
        self.stopped.set()

    def run(self):
        next_call = time.time()
        while not self.stopped.is_set():
            self.func()  # Target activity.
            next_call = next_call + self.interval
            # Block until beginning of next interval (unless canceled).
            self.stopped.wait(next_call - time.time())
            
def my_function():
    sensors = [1,2,3,4,5,6,7,8,9,10]
    for ss in sensors:
        value = round(random.uniform(-10,10),4)
        if value < 0:
            Path.insert_one({"timestamp": datetime.datetime.now(),"sensor":ss,"status":"bad","value": value})
        else:
            Path.insert_one({"timestamp": datetime.datetime.now(),"sensor":ss,"status":"good","value": value})


@sensor.post('/post-time')
async def post_time():
    # Start test a few secs from now.
    start_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
    run_time = datetime.timedelta(minutes=2)  # How long to iterate function.
    end_time = start_time + run_time

    assert start_time > datetime.datetime.now(), 'Start time must be in future'

    timed_calls = TimedCalls(my_function, 10)  # Thread to call function every 10 secs.

    # print(f'waiting until {start_time.strftime("%H:%M:%S")} to begin...')
    wait_time = start_time - datetime.datetime.now()
    time.sleep(wait_time.total_seconds())

    print('starting')
    timed_calls.start()  # Start thread.
    while datetime.datetime.now() < end_time:
        time.sleep(1)  # Twiddle thumbs while waiting.
    print('done')
    timed_calls.cancel()
    return {
        "message":"success"
    }

@sensor.post('/add-data')
async def add_data(data_sensor: Datasensor):
    time_now = datetime.now()
    SENSOR = [1,2,3,4,5,6,7,8,9,10]
    
    Path.insert_one(dict(data_sensor))
    return Data_Sensor_Entity(Path.find_one({"sensor":data_sensor.sensor}))

@sensor.get('/timestamp')
async def timestamp():
    time_now = datetime.now()
    m = time.time()
    end_time = 60*5
    # print(datetime.now())
    while True:
        current_time = time.time()
        i = 1
        if (current_time - m) == 60:
            print(i)
            m = current_time
        if i == 3:
            print(i) 
            break
    # print(m)
    return datetime.now()

