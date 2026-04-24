import weakref


class Event:
    def __init__(self):
        self.subscribers = weakref.WeakSet()

    def subscribe(self, fn):
        self.subscribers.add(fn)

    def unsubscribe(self, fn):
        self.subscribers.discard(fn)

    def notify(self, *args, **kwargs):
        for fn in list(self.subscribers):
            fn(*args, **kwargs)


def handler1(msg):
    print("Handler1 received:", msg)


def handler2(msg):
    print("Handler2 received:", msg)


evt = Event()
evt.subscribe(handler1)
evt.subscribe(handler2)
evt.notify("Hello Observers")


evt.unsubscribe(handler2)
evt.notify("Another message")
