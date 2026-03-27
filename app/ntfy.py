import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()

class NtfyClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.ntfy_url)
    
    async def send_notification(self, title: str, message: str, actions: list[dict] = None):
        headers = {
            "Title": title.encode('utf-8').decode('iso-8859-1', errors='ignore')
        }
        if actions:
            headers["Actions"] = ",".join(self._format_actions(actions))
            
        try:
            response = await self.client.post("/", data=message.encode("utf-8"), headers=headers)
            response.raise_for_status()
            logger.info("Sent ntfy notification", title=title, status=response.status_code)
        except Exception as e:
            logger.error("Failed to send ntfy notification", error=str(e))

    def _format_actions(self, actions: list[dict]) -> list[str]:
        # Format: view, Open portal, https://home.nest.com, clear=true
        # Format: http, Snooze, https://webhook/snooze?id=1, POST, clear=true
        formatted = []
        for action in actions:
            if action["action"] == "http":
                # action, label, url, method, headers/body/clear
                formatted.append(f'http, {action["label"]}, {action["url"]}, {action.get("method", "POST")}, clear=true')
            elif action["action"] == "view":
                formatted.append(f'view, {action["label"]}, {action["url"]}, clear=true')
        return formatted

ntfy_client = NtfyClient()
