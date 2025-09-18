class EventBus:
    """Mini bus d'événements (pub/sub) très simple.

    - on(event, handler): s'abonner
    - off(event, handler): se désabonner
    - emit(event, **data): émettre
    """

    def __init__(self):
        self._handlers = {}

    def on(self, event_name, handler):
        self._handlers.setdefault(event_name, []).append(handler)

    def off(self, event_name, handler):
        if event_name in self._handlers:
            try:
                self._handlers[event_name].remove(handler)
            except ValueError:
                pass

    def emit(self, event_name, **data):
        for handler in self._handlers.get(event_name, []):
            try:
                handler(data)
            except Exception:
                # Ne pas faire planter le jeu si un handler échoue
                pass


