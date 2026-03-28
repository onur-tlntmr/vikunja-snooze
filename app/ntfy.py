import httpx
import structlog
from app.config import settings

logger = structlog.get_logger()


class NtfyClient:
    def __init__(self):
        self.publish_url = settings.ntfy_url.strip().rstrip("/")
        self.client = httpx.AsyncClient()

    async def send_notification(
        self,
        title: str,
        message: str,
        actions: list[dict] | None = None,
    ) -> None:
        headers = {
            "Title": self._encode_header_value(title),
        }

        if actions:
            headers["Actions"] = "; ".join(self._format_actions(actions))

        try:
            response = await self.client.post(
                self.publish_url,
                content=message.encode("utf-8"),
                headers=headers,
            )
            response.raise_for_status()

            logger.info(
                "Sent ntfy notification",
                title=title,
                publish_url=self.publish_url,
                status=response.status_code,
                response_text=response.text,
                headers=headers,
            )
        except Exception as e:
            logger.error(
                "Failed to send ntfy notification",
                error=str(e),
                publish_url=self.publish_url,
                headers=headers,
            )

    def _format_actions(self, actions: list[dict]) -> list[str]:
        formatted: list[str] = []

        for action in actions:
            action_type = action.get("action")

            if action_type == "http":
                formatted.append(
                    f"http, {action['label']}, {action['url']}, "
                    f"method={action.get('method', 'POST')}, clear=true"
                )
            elif action_type == "view":
                formatted.append(
                    f"view, {action['label']}, {action['url']}, clear=true"
                )

        return formatted

    @staticmethod
    def _encode_header_value(value: str) -> str:
        return value.encode("utf-8").decode("iso-8859-1", errors="ignore")


ntfy_client = NtfyClient()
