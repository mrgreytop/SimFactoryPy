import simpy


class MonitorContainer(simpy.Container):

    def __init__(self, env: simpy.Environment, capacity: int = 0, 
        init: int = 0, parent: str = ""):

        self.parent = parent
        self.data = []
        super().__init__(env, capacity=capacity, init=init)

    def monitor(self):
        time = self._env.now
        level = self.level
        def event_callback(event):
            self.data.append({
                "Parent":self.parent,
                "Event":str(event),
                "Start Time":time,
                "End Time":self._env.now,
                "Start Level":level,
                "End Level":self.level
            })
        return event_callback


    def put(self, amount):
        monitor_callback = self.monitor()

        putEvent = super().put(amount)
        putEvent.callbacks.insert(0, monitor_callback)

        return putEvent


    def get(self, amount):
        monitor_callback = self.monitor()

        getEvent = super().get(amount)
        getEvent.callbacks.insert(0, monitor_callback)

        return getEvent


class MonitorStore(simpy.Store):

    def __init__(self, env: simpy.Environment, capacity:int = 0, parent: str = ""):
        self.parent = parent
        self.data = []
        super().__init__(env, capacity = capacity)


    def __len__(self):
        return len(self.items)

    @property
    def level(self):
        return len(self)


    def monitor(self, change):
        time = self._env.now
        level = len(self)
        def event_callback(event):
            self.data.append({
                "Parent":self.parent,
                "Event":str(event),
                "Start Time":time,
                "End Time":self._env.now,
                "Start Level":level,
                "End Level":len(self),
                "Change":change
            })
        return event_callback

    def put(self, item):
        monitor_callback = self.monitor(1)

        putEvent = super().put(item)
        putEvent.callbacks.insert(0, monitor_callback)

        return putEvent


    def get(self):
        monitor_callback = self.monitor(-1)

        getEvent = super().get()
        getEvent.callbacks.insert(0, monitor_callback)

        return getEvent