#!/usr/bin/env python3
"""WhatsApp integration for JarvisOS via Green API.

Two entry points:
  read_chat(chat_id, limit=None)   — fetch message history
  on_message(payload)              — webhook handler, auto-processes incoming messages

Usage (CLI):
  python3 whatsapp_skill.py history --chat <chat_id> [--limit 50]
  python3 whatsapp_skill.py send --chat <chat_id> --text "hello"
  python3 whatsapp_skill.py status

Env vars (loaded via load-env.sh):
  GREENAPI_INSTANCE_ID
  GREENAPI_API_TOKEN
  JARVIS_WHATSAPP_CHAT_ID   — chat ID to listen on (e.g. 34647001054@c.us)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[2]
WIKI_SOURCES = ROOT / "wiki" / "sources"
RAW_QUEUE = ROOT / "raw" / "ingest_queue"
RAW_ARCHIVE = ROOT / "raw" / "archive" / "ingest_queue"

# ── Green API client ──────────────────────────────────────────────────────────

class GreenAPIClient:
    def __init__(self) -> None:
        self.instance_id = os.environ.get("GREENAPI_INSTANCE_ID", "")
        self.token = os.environ.get("GREENAPI_API_TOKEN", "")
        if not self.instance_id or not self.token:
            raise RuntimeError(
                "GREENAPI_INSTANCE_ID and GREENAPI_API_TOKEN must be set.\n"
                "Run: source ~/toolbox/secrets/load-env.sh"
            )
        self.base = f"https://api.green-api.com/waInstance{self.instance_id}"

    def _get(self, method: str) -> Any:
        url = f"{self.base}/{method}/{self.token}"
        req = Request(url)
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())

    def _post(self, method: str, body: dict) -> Any:
        url = f"{self.base}/{method}/{self.token}"
        data = json.dumps(body).encode()
        req = Request(url, data=data, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())

    def state(self) -> str:
        return self._get("getStateInstance").get("stateInstance", "unknown")

    def get_chat_history(self, chat_id: str, limit: int | None = None) -> list[dict]:
        body: dict = {"chatId": chat_id}
        if limit:
            body["count"] = limit
        return self._post("getChatHistory", body)

    def send_message(self, chat_id: str, text: str) -> dict:
        return self._post("sendMessage", {"chatId": chat_id, "message": text})

    def receive_notification(self) -> dict | None:
        result = self._get("receiveNotification")
        return result if result else None

    def delete_notification(self, receipt_id: int) -> bool:
        url = f"{self.base}/deleteNotification/{self.token}/{receipt_id}"
        req = Request(url, method="DELETE")
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()).get("result", False)

    def set_webhook(self, url: str) -> dict:
        return self._post("setSettings", {"webhookUrl": url})


# ── Content detection ────────────────────────────────────────────────────────

URL_RE = re.compile(r"https?://[^\s]+")

def detect_content_type(text: str) -> str:
    if re.search(r"youtube\.com|youtu\.be", text):
        return "youtube"
    if re.search(r"instagram\.com", text):
        return "instagram"
    if URL_RE.search(text):
        return "url"
    return "text"


def archive_queue_file(path: Path) -> Path:
    archive_dir = RAW_ARCHIVE / datetime.now(timezone.utc).date().isoformat()
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / path.name
    counter = 2
    while target.exists():
        target = archive_dir / f"{path.stem}-{counter}{path.suffix}"
        counter += 1
    shutil.move(str(path), str(target))
    return target


# ── Message processing ───────────────────────────────────────────────────────

def process_message(client: GreenAPIClient, chat_id: str, text: str) -> str:
    """Process an incoming message: detect content type and route to pipeline."""
    text = text.strip()
    if not text:
        return ""

    content_type = detect_content_type(text)
    url_match = URL_RE.search(text)
    url = url_match.group(0) if url_match else None

    # Drop into ingest queue for sync_watcher to pick up
    RAW_QUEUE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    if content_type in ("youtube", "instagram", "url") and url:
        queue_file = RAW_QUEUE / f"{stamp}-whatsapp-{content_type}.txt"
        queue_file.write_text(url, encoding="utf-8")
        reply = f"✓ URL detectada ({content_type}). Procesando en wiki/sources/..."
    else:
        queue_file = RAW_QUEUE / f"{stamp}-whatsapp-text.txt"
        queue_file.write_text(text, encoding="utf-8")
        reply = "✓ Texto recibido. Guardando en wiki/sources/..."

    # Try to process immediately. URLs use the rich analyzer; plain text uses
    # the lightweight file ingestor.
    analyzer = ROOT / "tools" / "skills" / "content_analyzer.py"
    ingestor = ROOT / "tools" / "skills" / "chat_ingestor.py"
    try:
        if url:
            result = subprocess.run(
                [sys.executable, str(analyzer), url, "--origin", "whatsapp"],
                capture_output=True, text=True, timeout=120,
            )
        else:
            result = subprocess.run(
                [sys.executable, str(ingestor), str(queue_file), "--archive"],
                capture_output=True, text=True, timeout=30,
            )
        if result.returncode == 0:
            out = json.loads(result.stdout.strip())
            note_name = Path(out["output"]).name
            if url and queue_file.exists():
                archive_queue_file(queue_file)
            reply = f"✓ Nota creada: {note_name}"
        else:
            reply = f"⚠️ Nota en cola — se procesará en el próximo ciclo."
    except Exception:
        reply = "⚠️ En cola para procesamiento."

    client.send_message(chat_id, reply)
    return reply


def on_message(client: GreenAPIClient, payload: dict) -> None:
    """Webhook/polling handler. Called for each incoming notification."""
    body = payload.get("body", {})
    msg_type = body.get("typeWebhook")

    if msg_type != "incomingMessageReceived":
        return

    sender_data = body.get("senderData", {})
    message_data = body.get("messageData", {})

    chat_id = sender_data.get("chatId", "")
    text_data = message_data.get("textMessageData", {})
    text = text_data.get("textMessage", "")

    # Only process messages from the configured Jarvis chat
    jarvis_chat = os.environ.get("JARVIS_WHATSAPP_CHAT_ID", "")
    if jarvis_chat and chat_id != jarvis_chat:
        return

    if text:
        process_message(client, chat_id, text)


# ── History reader ────────────────────────────────────────────────────────────

def read_chat(chat_id: str, limit: int | None = None) -> list[dict]:
    """Fetch chat history. Returns list of message dicts."""
    client = GreenAPIClient()
    messages = client.get_chat_history(chat_id, limit=limit)
    return messages


def print_history(messages: list[dict], limit: int | None = None) -> None:
    shown = messages[:limit] if limit else messages
    for msg in shown:
        ts = msg.get("timestamp", 0)
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
        sender = "Tú" if msg.get("type") == "outgoing" else msg.get("senderId", "?")
        text = msg.get("textMessage") or msg.get("caption") or f"[{msg.get('typeMessage', 'media')}]"
        print(f"[{dt}] {sender}: {text}")


# ── Polling loop (fallback when no public webhook) ────────────────────────────

def poll_loop(client: GreenAPIClient, interval: int = 3) -> None:
    """Poll Green API for new notifications. Use when webhook is not available."""
    import time
    print(f"Polling for messages (interval={interval}s). Ctrl+C to stop.")
    while True:
        try:
            notification = client.receive_notification()
            if notification:
                receipt_id = notification.get("receiptId")
                on_message(client, notification)
                if receipt_id:
                    client.delete_notification(receipt_id)
        except URLError as e:
            print(f"Network error: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        time.sleep(interval)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")

    # status
    sub.add_parser("status", help="Check Green API instance state")

    # history
    p_hist = sub.add_parser("history", help="Read chat history")
    p_hist.add_argument("--chat", required=True, help="Chat ID (e.g. 34647001054@c.us)")
    p_hist.add_argument("--limit", type=int, default=None, help="Max messages to fetch")
    p_hist.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")

    # send
    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("--chat", required=True)
    p_send.add_argument("--text", required=True)

    # poll
    p_poll = sub.add_parser("poll", help="Poll for incoming messages and process them")
    p_poll.add_argument("--interval", type=int, default=3, help="Polling interval in seconds")

    # webhook
    p_wh = sub.add_parser("set-webhook", help="Configure Green API webhook URL")
    p_wh.add_argument("--url", required=True, help="Public URL of your webhook endpoint")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    client = GreenAPIClient()

    if args.cmd == "status":
        state = client.state()
        print(f"Instance state: {state}")

    elif args.cmd == "history":
        messages = client.get_chat_history(args.chat, limit=args.limit)
        if args.as_json:
            print(json.dumps(messages, ensure_ascii=False, indent=2))
        else:
            print_history(messages, limit=args.limit)

    elif args.cmd == "send":
        result = client.send_message(args.chat, args.text)
        print(json.dumps(result, ensure_ascii=False))

    elif args.cmd == "poll":
        poll_loop(client, interval=args.interval)

    elif args.cmd == "set-webhook":
        result = client.set_webhook(args.url)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
