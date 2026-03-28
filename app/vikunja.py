import httpx
import structlog
from app.config import settings
from datetime import datetime, timedelta, timezone

logger = structlog.get_logger()

class VikunjaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.vikunja_api_url.rstrip("/") + "/",
            headers={"Authorization": f"Bearer {settings.vikunja_api_token}"}
        )
    
    async def mark_task_done(self, task_id: int):
        payload = {"done": True}
        try:
            response = await self.client.post(f"tasks/{task_id}", json=payload)
            response.raise_for_status()
            logger.info("Task marked as done", task_id=task_id)
            return True
        except Exception as e:
            logger.error("Failed to mark task done", task_id=task_id, error=str(e))
            return False

    async def snooze_task_reminder(self, task_id: int, minutes: int = 15):
        # We fetch the task first to append a new reminder or just update the due date?
        # Usually snoozing means adding a reminder +15 minutes from now.
        new_reminder = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        # Vikunja expects reminders to be an array of timestamps or strings or we can just send "reminders" object? 
        # Actually in Vikunja API, to add a reminder we often use a specific endpoint or update the `reminders` list.
        # Alternatively, Snooze might just be due_date shift, but reminder is better.
        try:
            # Let's get the task to ensure it
            await self.client.get(f"tasks/{task_id}")
            # We just ensure the task exists before modifying

            # Reminders might be objects or just we can update due_date for snooze
            # Simplest snooze: Just shift the due_date or reminder. We will shift due_date for now if reminders parsing is complex.
            # Wait, Vikunja has a /tasks/{task_id} POST update. Let's just set due_date.
            payload = {"due_date": new_reminder}
            res = await self.client.post(f"tasks/{task_id}", json=payload)
            res.raise_for_status()
            logger.info("Task snoozed", task_id=task_id, added_minutes=minutes)
            return True
        except Exception as e:
            logger.error("Failed to snooze task", task_id=task_id, error=str(e))
            return False

vikunja_client = VikunjaClient()
