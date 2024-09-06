from typing import Dict, Callable, List, Any
from asyncio import Queue

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = Queue()

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event_type: str, data: Any):
        await self.event_queue.put((event_type, data))

    async def process_events(self):
        while True:
            event_type, data = await self.event_queue.get()
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    await callback(data)
            self.event_queue.task_done()

event_bus = EventBus()