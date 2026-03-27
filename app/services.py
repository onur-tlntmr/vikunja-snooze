import structlog
from app.models import VikunjaWebhookPayload
from app.ntfy import ntfy_client
from app.vikunja import vikunja_client
import os

logger = structlog.get_logger()

action_base_url = os.getenv("ACTION_BASE_URL", "http://localhost:8000")

async def process_webhook(payload: VikunjaWebhookPayload):
    task = payload.data.task
    event_name = payload.event_name
    
    title = f"Vikunja: {task.title}"
    message = f"Event: {event_name}\nTask ID: {task.id}"
    
    if task.description:
        message += f"\n\n{task.description}"
    if task.due_date:
        message += f"\nDue Date: {task.due_date}"

    # Ntfy and Android support max 3 action buttons.
    # We add Markdown links to the message body for the full list of snooze options.
    snooze_options = [
        ("5m", 5), ("15m", 15), ("30m", 30), 
        ("1h", 60), ("4h", 240), ("6h", 360), 
        ("12h", 720), ("1d", 1440)
    ]
    
    md_links = " | ".join(
        [f"[{label}]({action_base_url}/actions/snooze?task_id={task.id}&minutes={mins})" for label, mins in snooze_options]
    )
    
    message += f"\n\n**Snooze Options:**\n{md_links}\n"
    message += f"**Complete:** [Mark Task Done]({action_base_url}/actions/complete?task_id={task.id})"

    # Action buttons for Ntfy (Limited to 3)
    actions = [
        {
            "action": "http",
            "label": "Complete",
            "url": f"{action_base_url}/actions/complete?task_id={task.id}",
            "method": "POST"
        },
        {
            "action": "http",
            "label": "Snooze 15m",
            "url": f"{action_base_url}/actions/snooze?task_id={task.id}&minutes=15",
            "method": "POST"
        },
        {
            "action": "http",
            "label": "Snooze 1d",
            "url": f"{action_base_url}/actions/snooze?task_id={task.id}&minutes=1440",
            "method": "POST"
        }
    ]
    
    await ntfy_client.send_notification(title, message, actions)
    logger.info("Webhook processed", task_id=task.id)

async def handle_action_snooze(task_id: int, minutes: int = 15):
    logger.info("Handling snooze action", task_id=task_id, minutes=minutes)
    return await vikunja_client.snooze_task_reminder(task_id, minutes)

async def handle_action_complete(task_id: int):
    logger.info("Handling complete action", task_id=task_id)
    return await vikunja_client.mark_task_done(task_id)
