#!/usr/bin/env python3
"""
旺仔任务板 (WangZai TaskBoard) v1.0
A lightweight task management system for 老大 and 旺仔.

Usage:
  python taskboard.py add "task description" [--priority high|medium|low] [--tag TAG]
  python taskboard.py list [--status open|done|all] [--tag TAG]
  python taskboard.py done TASK_ID
  python taskboard.py remove TASK_ID
  python taskboard.py stats
  python taskboard.py report  (generates a formatted report for Feishu)
"""

import json
import os
import sys
import argparse
from datetime import datetime

BOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
TAG_EMOJI = {
    "bug": "🐛", "feature": "✨", "idea": "💡", "build": "🛠️",
    "paper": "📚", "urgent": "🚨", "learn": "📖", "infra": "⚙️",
}


def load_tasks():
    if os.path.exists(BOARD_FILE):
        with open(BOARD_FILE, "r") as f:
            return json.load(f)
    return {"next_id": 1, "tasks": []}


def save_tasks(data):
    with open(BOARD_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_task(args):
    data = load_tasks()
    task = {
        "id": data["next_id"],
        "desc": args.desc,
        "priority": args.priority,
        "tag": args.tag,
        "status": "open",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed": None,
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save_tasks(data)
    emoji = PRIORITY_EMOJI.get(task["priority"], "⚪")
    tag_e = TAG_EMOJI.get(task["tag"], f"#{task['tag']}") if task["tag"] else ""
    print(f"✅ 任务 #{task['id']} 已添加: {emoji} {task['desc']} {tag_e}")
    return task


def list_tasks(args):
    data = load_tasks()
    tasks = data["tasks"]
    if args.status != "all":
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.tag:
        tasks = [t for t in tasks if t.get("tag") == args.tag]
    if not tasks:
        print("📋 没有找到任务")
        return []

    # Sort: high > medium > low, then by id
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 3), t["id"]))

    print(f"📋 任务列表 ({len(tasks)} 项)\n")
    for t in tasks:
        emoji = PRIORITY_EMOJI.get(t["priority"], "⚪")
        status = "✅" if t["status"] == "done" else "⬜"
        tag_e = TAG_EMOJI.get(t.get("tag", ""), f"#{t['tag']}") if t.get("tag") else ""
        print(f"  {status} #{t['id']} {emoji} {t['desc']} {tag_e}")
        if t["status"] == "done" and t.get("completed"):
            print(f"       完成于 {t['completed']}")
    return tasks


def done_task(args):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == args.task_id:
            t["status"] = "done"
            t["completed"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(data)
            print(f"🎉 任务 #{t['id']} 已完成: {t['desc']}")
            return t
    print(f"❌ 找不到任务 #{args.task_id}")
    return None


def remove_task(args):
    data = load_tasks()
    for i, t in enumerate(data["tasks"]):
        if t["id"] == args.task_id:
            removed = data["tasks"].pop(i)
            save_tasks(data)
            print(f"🗑️ 任务 #{removed['id']} 已删除: {removed['desc']}")
            return removed
    print(f"❌ 找不到任务 #{args.task_id}")
    return None


def stats(args):
    data = load_tasks()
    tasks = data["tasks"]
    total = len(tasks)
    open_count = sum(1 for t in tasks if t["status"] == "open")
    done_count = sum(1 for t in tasks if t["status"] == "done")
    high = sum(1 for t in tasks if t["status"] == "open" and t["priority"] == "high")
    tags = {}
    for t in tasks:
        if t.get("tag"):
            tags[t["tag"]] = tags.get(t["tag"], 0) + 1

    print("📊 任务统计\n")
    print(f"  总计: {total} 项")
    print(f"  待办: {open_count} 项 (🔴 紧急: {high})")
    print(f"  完成: {done_count} 项")
    if total > 0:
        rate = done_count / total * 100
        bar_len = 20
        filled = int(bar_len * done_count / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  完成率: [{bar}] {rate:.0f}%")
    if tags:
        print(f"\n  标签分布:")
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            emoji = TAG_EMOJI.get(tag, "#")
            print(f"    {emoji} {tag}: {count}")


def report(args):
    """Generate a formatted report suitable for Feishu messaging."""
    data = load_tasks()
    tasks = data["tasks"]
    open_tasks = [t for t in tasks if t["status"] == "open"]
    done_tasks = [t for t in tasks if t["status"] == "done"]

    priority_order = {"high": 0, "medium": 1, "low": 2}
    open_tasks.sort(key=lambda t: (priority_order.get(t["priority"], 3), t["id"]))

    lines = [f"📋 旺仔任务板 | {datetime.now().strftime('%Y-%m-%d')}", ""]

    if open_tasks:
        lines.append(f"⬜ 待办 ({len(open_tasks)} 项)")
        for t in open_tasks:
            emoji = PRIORITY_EMOJI.get(t["priority"], "⚪")
            tag_e = TAG_EMOJI.get(t.get("tag", ""), f"#{t['tag']}") if t.get("tag") else ""
            lines.append(f"  {emoji} #{t['id']} {t['desc']} {tag_e}")
        lines.append("")

    if done_tasks:
        recent_done = sorted(done_tasks, key=lambda t: t.get("completed", ""), reverse=True)[:5]
        lines.append(f"✅ 最近完成 ({len(done_tasks)} 项)")
        for t in recent_done:
            tag_e = TAG_EMOJI.get(t.get("tag", ""), f"#{t['tag']}") if t.get("tag") else ""
            lines.append(f"  ✅ #{t['id']} {t['desc']} {tag_e}")
        lines.append("")

    total = len(tasks)
    if total > 0:
        rate = len(done_tasks) / total * 100
        filled = int(10 * len(done_tasks) / total)
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"进度: [{bar}] {rate:.0f}% ({len(done_tasks)}/{total})")

    output = "\n".join(lines)
    print(output)
    return output


def main():
    parser = argparse.ArgumentParser(description="旺仔任务板")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add")
    p_add.add_argument("desc", help="任务描述")
    p_add.add_argument("--priority", "-p", default="medium", choices=["high", "medium", "low"])
    p_add.add_argument("--tag", "-t", default=None)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", "-s", default="open", choices=["open", "done", "all"])
    p_list.add_argument("--tag", "-t", default=None)

    p_done = sub.add_parser("done")
    p_done.add_argument("task_id", type=int)

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("task_id", type=int)

    sub.add_parser("stats")
    sub.add_parser("report")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"add": add_task, "list": list_tasks, "done": done_task,
     "remove": remove_task, "stats": stats, "report": report}[args.command](args)


if __name__ == "__main__":
    main()
