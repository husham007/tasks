import logging
import sys
from random import random
from threading import Thread
from datetime import datetime, timedelta
import time
import requests


log = logging.getLogger('XKCD_SERVICE_SCHEDULER')
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(levelname)-10s %(name)-10s %(asctime)s %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(log_format)
log.addHandler(ch)

class Event:
    def __init__(self, action, enabled=True, threaded=False):
        self.action = action
        self.threaded = threaded
        self._enabled = enabled

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        log.info('Updating event, setting enabled = %r' % value)
        self._enabled = value

    def match_time(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return False

    def check(self, t):
        if self.match_time(t):
            log.info('Time matched, running task')
            self.run()

    def run(self):
        if self.threaded:
            Thread(target=self.run_action).start()
        else:
            self.run_action()

    def run_action(self):
        try:
            return self.action()
        except Exception as e:
            log.exception('Scheduler exception when running action %s: %s' % (e.__class__.__name__, str(e)))


class EveryEvent(Event):
    def __init__(self, action, ev_minutes=0, ev_hours=0, ev_days=0, enabled=True, threaded=False):
        Event.__init__(self, action=action, enabled=enabled, threaded=threaded)
        self._next_run = None
        self.set_time_params(ev_minutes, ev_hours, ev_days)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return

        log.info('Updating EveryEvent, setting enabled = %r' % value)
        self._enabled = value
        if self._enabled:
            self._next_run = datetime(*datetime.now().timetuple()[:5]) + timedelta(minutes=self._ev_minutes,
                                                                                   hours=self._ev_hours,
                                                                                   days=self._ev_days)
        else:
            self._next_run = None

    @property
    def next_run(self):
        if not self.enabled:
            return None

        return self._next_run

    def set_time_params(self, ev_minutes=0, ev_hours=0, ev_days=0):
        self._ev_minutes = ev_minutes
        self._ev_hours = ev_hours
        self._ev_days = ev_days
        self._next_run = datetime(*datetime.now().timetuple()[:5]) + timedelta(minutes=self._ev_minutes,
                                                                               hours=self._ev_hours, days=self._ev_days)
        log.info('Updating EveryEvent, evMinutes: %r, evHours: %r, evDays: %r' % (ev_minutes, ev_hours, ev_days))

    def match_time(self, t):
        """Return True if this event should trigger at the specified datetime"""
        if not self.enabled:
            return False

        if not self._next_run:
            self._next_run = t + timedelta(minutes=self._ev_minutes, hours=self._ev_hours, days=self._ev_days)

        if t >= self._next_run:
            self._next_run = t + timedelta(minutes=self._ev_minutes, hours=self._ev_hours, days=self._ev_days)
            return True

        return False


class CronTab(Thread):
    def __init__(self, *events):
        Thread.__init__(self)
        self._terminated = False
        self._events = list(events) if events else []

    @property
    def terminated(self):
        """Is terminated property"""
        return self._terminated

    def add_events(self, *events):
        """Adds event(s) to the events list"""
        self._events += list(events)

    def remove_events(self, *events):
        """Removes event(s) from the events list"""
        for event in events:
            if event in self._events:
                self._events.remove(event)

    def remove_all_events(self):
        """Removes all events"""
        self._events = []

    def start(self):
        """Starts the crontab"""
        self._terminated = False
        return Thread.start(self)

    def terminate(self, join=True):
        """Terminate crontab"""
        self.remove_all_events()
        self._terminated = True
        if join:
            self.join()

    def run(self):
        """Internal method of crontab"""
        log.info('Starting CronTab')

        # Initial run
        t = datetime(*datetime.now().timetuple()[:5])
        self.check_events(t)

        # Check every minute if event should be run or not
        t = datetime(*datetime.now().timetuple()[:5])

        while not self.terminated:
            t += timedelta(minutes=1)
            while datetime.now() < t:
                time_dif = t - datetime.now()
                # print(time_dif, time_dif.seconds, time_dif.microseconds / 1000000.0)
                # print(time_dif.seconds + time_dif.microseconds / 1000000.0)
                time.sleep(time_dif.seconds + time_dif.microseconds / 1000000.0)

            self.check_events(t)

        log.info('CronTab terminated')

    def check_events(self, t):
        """Check events"""
        log.debug('Checking events')
        for event in self._events:
            event.check(t)



