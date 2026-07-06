#!/usr/bin/env python3
"""Query Xiaohei Daily Assistant after refreshing its live API docs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

BASE_URL = "http://192.168.11.212:8088"

INTENT_HINTS = {
    "timeline": ["timeline", "时间线", "工作记录", "工作时间线"],
    "report": ["report", "报告", "日报", "周报", "月报", "工作报告"],
    "heat-map": ["heat", "heat-map", "热力", "热力图", "时段"],
    "app-usage": ["app", "usage", "应用", "软件", "使用时长", "app usage"],
}


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8")


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def parse_get_endpoints(markdown: str) -> dict[str, str]:
    endpoints: dict[str, str] = {}
    for match in re.finditer(r"`GET\s+([^`]+)`", markdown):
        path = match.group(1).strip()
        if path.startswith("/"):
            key = path.strip("/").split("/")[-1] or "docs"
            endpoints[key] = path
    return endpoints


def choose_intent(intent: str | None, query: str | None) -> str:
    if intent:
        return intent
    text = (query or "").lower()
    for candidate, hints in INTENT_HINTS.items():
        if any(hint.lower() in text for hint in hints):
            return candidate
    raise SystemExit("Unable to infer intent. Use --intent timeline|report|heat-map|app-usage.")


def choose_endpoint(intent: str, endpoints: dict[str, str]) -> str:
    preferred = {
        "timeline": ["timeline"],
        "report": ["report"],
        "heat-map": ["heat-map", "heat"],
        "app-usage": ["app-usage", "usage"],
    }[intent]
    for key in preferred:
        if key in endpoints:
            return endpoints[key]
    for path in endpoints.values():
        if any(key in path for key in preferred):
            return path
    raise SystemExit(f"Live API docs do not expose an endpoint for intent: {intent}")


def build_url(path: str, start_date: str | None, end_date: str | None) -> str:
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    query = urllib.parse.urlencode(params)
    return f"{BASE_URL}{path}" + (f"?{query}" if query else "")


def human_duration(seconds: int | float | None) -> str:
    if seconds is None:
        return "-"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def compact_time(value: str | None) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def render(intent: str, url: str, payload: dict[str, Any]) -> str:
    code = payload.get("code")
    message = payload.get("message")
    if code != 0:
        return f"Request failed: code={code}, message={message}, endpoint={url}"

    data = payload.get("data")
    if not data:
        return f"No data returned.\n\nEndpoint: `{url}`"

    lines = [f"Endpoint: `{url}`", ""]
    if intent == "app-usage":
        lines.append("| App | Duration | First used | Last used |")
        lines.append("|---|---:|---|---|")
        for item in data:
            lines.append(
                f"| {item.get('appName', '-')} | {human_duration(item.get('totalDurationSec'))} | "
                f"{compact_time(item.get('firstUsedAt'))} | {compact_time(item.get('lastUsedAt'))} |"
            )
    elif intent == "timeline":
        for item in data:
            lines.append(
                f"- {compact_time(item.get('startTime'))} - {compact_time(item.get('endTime'))} "
                f"[{item.get('category', '-')}] {item.get('summary', '-')}"
            )
    elif intent == "report":
        for index, item in enumerate(data, start=1):
            lines.append(f"## {index}. {item.get('title', 'Untitled')}")
            lines.append(f"- Range: {item.get('startDate', '-')} to {item.get('endDate', '-')}")
            lines.append(f"- Status: {item.get('status', '-')}")
            lines.append("")
            lines.append(item.get("content") or "")
            lines.append("")
    elif intent == "heat-map":
        lines.append("| Date | Focus | Records | Top category | Active period | Hourly counts |")
        lines.append("|---|---:|---:|---|---|---|")
        for item in data:
            hourly = ",".join(str(n) for n in item.get("hourlyCounts", []))
            lines.append(
                f"| {item.get('date', '-')} | {item.get('focusMinutes', 0)}m | "
                f"{item.get('totalRecords', 0)} | {item.get('topCategory', '-')} | "
                f"{item.get('activePeriod', '-')} | `{hourly}` |"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", choices=["timeline", "report", "heat-map", "app-usage"])
    parser.add_argument("--query", help="Natural language query for lightweight intent detection.")
    parser.add_argument("--start-date", help="YYYY-MM-DD or YYYY-MM-DD HH:mm:ss")
    parser.add_argument("--end-date", help="YYYY-MM-DD or YYYY-MM-DD HH:mm:ss")
    parser.add_argument("--show-docs", action="store_true", help="Print fetched live API Markdown.")
    args = parser.parse_args()

    docs = fetch_text(f"{BASE_URL}/")
    if args.show_docs:
        print(docs)
        return 0

    endpoints = parse_get_endpoints(docs)
    intent = choose_intent(args.intent, args.query)
    path = choose_endpoint(intent, endpoints)
    url = build_url(path, args.start_date, args.end_date)
    payload = fetch_json(url)
    print(render(intent, url, payload))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
