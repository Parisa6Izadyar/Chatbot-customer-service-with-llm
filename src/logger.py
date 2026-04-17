from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "logs.csv"


class ChatLogger:
    def __init__(self, log_file: Path = LOG_FILE) -> None:
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.log_file.exists():
            with self.log_file.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "user_message",
                        "bot_response",
                        "intent",
                        "action",
                        "mode",
                    ]
                )

    def log(
        self,
        user_message: str,
        bot_response: str,
        intent: str,
        action: str,
        mode: str,
        timestamp: Optional[str] = None,
    ) -> None:
        if timestamp is None:
            timestamp = datetime.now().isoformat(timespec="seconds")

        with self.log_file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    timestamp,
                    user_message,
                    bot_response,
                    intent,
                    action,
                    mode,
                ]
            )


if __name__ == "__main__":
    logger = ChatLogger()
    logger.log(
        user_message="Where is my order?",
        bot_response="Please share your order number.",
        intent="order_status",
        action="ANSWER",
        mode="demo",
    )
    print(f"Test log written to: {LOG_FILE}")