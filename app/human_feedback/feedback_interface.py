import asyncio
from typing import Dict, Any

class HumanFeedbackInterface:
    def __init__(self):
        self.feedback_queue = asyncio.Queue()

    async def request_feedback(self, step: Dict[str, Any]):
        await self.feedback_queue.put(step)

    async def provide_feedback(self, feedback: str):
        await self.feedback_queue.put(feedback)

    async def get_next_feedback_request(self) -> Dict[str, Any]:
        return await self.feedback_queue.get()
    async def get_feedback(self, step: Dict[str, Any]) -> str:
        print(f"\nHuman feedback requested for step: {step}")
        print("Please provide your feedback (press Enter to submit):")
        
        # This is a simple implementation that works in console environments
        # For web-based or other interfaces, you'd implement a different mechanism
        feedback = await asyncio.get_event_loop().run_in_executor(None, input)
        return feedback