import structlog
from app.models import VikunjaWebhookPayload
from app.ntfy import ntfy_client
from app.vikunja import vikunja_client
from app.config import settings

logger = structlog.get_logger()

def get_action_url(path: str) -> str:
    base = settings.action_base_url.rstrip("/")
    if not (base.startswith("http://") or base.startswith("https://")):
        base = f"{settings.action_scheme}://{base}"
    return f"{base}{path}"

async def process_webhook(payload: VikunjaWebhookPayload):
    task = payload.data.task
    event_name = payload.event_name
    
    title = f"🔔 Vikunja: {task.title}"
    
    # Message Body Construction
    body_lines = [
        f"**Event:** {event_name}",
        f"**Task ID:** {task.id}"
    ]
    
    if task.due_date:
        formatted_due = task.due_date.strftime("%Y-%m-%d %H:%M")
        body_lines.append(f"📅 **Due:** {formatted_due}")
    
    if task.description:
        body_lines.append(f"\n{task.description}")

    body_lines.append("\n---")
    body_lines.append("**Snooze Options:**")
    
    snooze_options = [
        ("5m", 5), ("15m", 15), ("30m", 30), ("1h", 60),
        ("4h", 240), ("6h", 360), ("12h", 720), ("1d", 1440)
    ]
    
    # Group snooze options in rows of 4
    rows = []
    for i in range(0, len(snooze_options), 4):
        chunk = snooze_options[i:i+4]
        row = " · ".join(
            [f"[{label}]({get_action_url(f'/actions/snooze?task_id={task.id}&minutes={mins}')})" 
             for label, mins in chunk]
        )
        rows.append(row)
    
    body_lines.extend(rows)
    body_lines.append("---")
    body_lines.append(f"[✅ Mark Task Done]({get_action_url(f'/actions/complete?task_id={task.id}')})")
    
    message = "\n".join(body_lines)

    # Action buttons for Ntfy (Limited to 3)
    actions = [
        {
            "action": "http",
            "label": "Complete",
            "url": get_action_url(f"/actions/complete?task_id={task.id}"),
            "method": "POST"
        },
        {
            "action": "http",
            "label": "Snooze 15m",
            "url": get_action_url(f"/actions/snooze?task_id={task.id}&minutes=15"),
            "method": "POST"
        },
        {
            "action": "http",
            "label": "Snooze 1d",
            "url": get_action_url(f"/actions/snooze?task_id={task.id}&minutes=1440"),
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
