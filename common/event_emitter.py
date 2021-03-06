# -*- coding: utf-8 -*-
import asyncio
from collections.abc import Coroutine
from multiprocessing import Process


class EventEmitter(object):
    def __init__(self, loop=None):
        self._events = {}
        self._loop = loop or asyncio.get_event_loop()

    def _on(self, event, listener):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)

    def _once(self, event, listener):
        listener.is_once = True
        self._on(event, listener)

    def emit(self, event, *args, **kwargs):
        if event in self._events:
            # 'once' may delete items while iterating over listeners -> we use a copy
            listeners = self._events[event][:]
            for listener in listeners:
                if hasattr(listener, 'is_once') and listener.is_once:
                    self.remove(event, listener)
                # Isolate exception
                try:
                    r = listener(*args, **kwargs)
                    if isinstance(r, Coroutine):
                        asyncio.ensure_future(r, loop=self._loop)
                except Exception as e:
                    # Exceptions raised during run listener emit to event 'i_error',
                    # customer can process them outside.
                    self.emit('i_error', e, *args, **kwargs)

    def parallel_emit(self, event, *args, **kwargs):
        if event in self._events:
            # 'once' may delete items while iterating over listeners -> we use a copy
            listeners = self._events[event][:]
            for listener in listeners:
                if hasattr(listener, 'is_once') and listener.is_once:
                    self.remove(event, listener)
                p = Process(target=listener, args=args, kwargs=kwargs)
                p.start()
                p.join()

    def remove(self, event, listener):
        if event in self._events:
            events = self._events[event]
            if listener in events:
                events.remove(listener)

    def remove_all(self, event):
        if event in self._events:
            self._events[event] = []

    def count(self, event):
        return len(self._events[event]) if event in self._events else 0

    def on(self, event):
        def decorator(listener):
            self._on(event, listener)
            return listener

        return decorator

    def once(self, event):
        def decorator(listener):
            self._once(event, listener)
            return listener

        return decorator
