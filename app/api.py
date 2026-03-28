from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.models import VikunjaWebhookPayload
from app import services as notification_service
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request, payload: VikunjaWebhookPayload):
    logger.info("Received Vikunja Webhook", webhook_event=payload.event_name)
    try:
        await notification_service.process_webhook(payload)
        return {"status": "success"}
    except Exception as e:
        logger.error("Error processing webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.api_route("/actions/snooze", methods=["GET", "POST"])
async def action_snooze(task_id: int, minutes: int = 15):
    logger.info("Action requested: Snooze", task_id=task_id, minutes=minutes)
    success = await notification_service.handle_action_snooze(task_id, minutes)
    if success:
        return HTMLResponse(f"<h3>Task successfully snoozed for {minutes} minutes!</h3>")
    raise HTTPException(status_code=500, detail="Failed to snooze task")

@router.api_route("/actions/complete", methods=["GET", "POST"])
async def action_complete(task_id: int):
    logger.info("Action requested: Complete", task_id=task_id)
    success = await notification_service.handle_action_complete(task_id)
    if success:
        return HTMLResponse("<h3>Task marked as complete!</h3>")
    raise HTTPException(status_code=500, detail="Failed to mark task complete")
