from fastapi import APIRouter, Request, HTTPException
from app.models import VikunjaWebhookPayload
from app import services as notification_service
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request, payload: VikunjaWebhookPayload):
    logger.info("Received Vikunja Webhook", event=payload.event_name)
    try:
        await notification_service.process_webhook(payload)
        return {"status": "success"}
    except Exception as e:
        logger.error("Error processing webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/actions/snooze")
async def action_snooze(task_id: int, minutes: int = 15):
    logger.info("Action requested: Snooze", task_id=task_id, minutes=minutes)
    success = await notification_service.handle_action_snooze(task_id, minutes)
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Failed to snooze task")

@router.post("/actions/complete")
async def action_complete(task_id: int):
    logger.info("Action requested: Complete", task_id=task_id)
    success = await notification_service.handle_action_complete(task_id)
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Failed to mark task complete")
