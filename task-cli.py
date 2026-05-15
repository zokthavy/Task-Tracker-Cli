from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DATA_FLILENAME = Path("tasks.json")

VALID_STATUSES = frozenset({"pending", "in-progress", "completed"})

class TaskCliError(Exception):
    """User-facing error with a clear message."""

def data_path() -> Path:
    return Path.cwd() / DATA_FLILENAME

def default_data() -> dict[str, Any]:
    return {"next_id": 1, "tasks": []}

def validate_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TaskCliError("Invalid tasks file: root must be a JSON object.")
    if "tasks" not in data or "next_id" not in data:
        raise TaskCliError("Invalid tasks file: missing 'tasks' or 'next_id'.")
    tasks = data["tasks"]
    next_id = data["next_id"]
    if not isinstance(tasks, list):
        raise TaskCliError("Invalid tasks file: 'tasks' must be a list.")
    if not isinstance(next_id, int) or next_id < 1:
        raise TaskCliError("Invalid tasks file: 'next_id' must be a positive integer.")
    seen: set[int] = set()
    for i, item in enumerate(tasks):
        if not isinstance(item, dict):
            raise TaskCliError(f"Invalid tasks file: task at index {i} is not an object.")
        for key in ("id", "description", "status"):
            if key not in item:
                raise TaskCliError(f"Invalid tasks file: task at index {i} missing '{key}'.")

        tid = item["id"]
        if not isinstance(tid, int):
            raise TaskCliError(f"Invalid tasks file: task id must be integer (task {i}).")
        if tid in seen:
            raise TaskCliError(f"Invalid tasks file: duplicate task id {tid}.")
        seen.add(tid)
        desc = item["description"]
        if not isinstance(desc, str):
            raise TaskCliError("Invalid tasks file: description must be a string.")
        status = item["status"]
        if status not in VALID_STATUSES:
            raise TaskCliError(
                f"Invalid tasks file: unknown status '{status!r} for id {tid}."
            )
    return data

def load_data() -> dict[str, Any]:
    path = data_path()
    if not path.exists():
        return default_data()
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise TaskCliError(f"Cannot read {path}: {e}") from e
    if not raw.strip():
        return default_data()
    try: 
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise TaskCliError(f"Invalid JSON in {path}: {e}") from e
    return validate_data(data)

def save_data(data: dict[str, Any]) -> None:
    path = data_path()
    tmp = path.with_suffix(".tmp")
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    except OSError as e:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
            raise TaskCliError(f"Cannot save tasks to {path}: {e}") from e

def find_task_index(tasks: list[dic[str, Any]], task_id: int) -> int:
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            return i
        raise TaskCliError(f"No task with id {task_id}.")

def cmd_add(args: argparse.Namespace) -> None:
    desc = " ".join(args.description).strip()
    if not desc:
        raise TaskCliError("Task description cannot be empty.")
    data = load_data()
    tid = data["next_id"]
    data["tasks"].append({"id": tid, "description": desc, "status": "pending"})
    data["next_id"] = tid + 1
    save_data(data)
    print(f'Added task {tid}: {desc}')

def cmd_update(args: argparse.Namespace) -> None:
    desc = " ".join(args.description).strip()
    if not desc:
        raise TaskCliError("Task description cannot be empty.")
    data = load_data()
    index = find_task_index(data["tasks"], args.id)
    data["tasks"][index]["description"] = desc
    save_data(data)
    print(f'Updated task {args.id}: {desc}')

def cmd_delete(args: argparse.Namespace) -> None:
    data = load_data()
    index = find_task_index(data["tasks"], args.id)
    removed = data["tasks"].pop(index)
    save_data(data)
    print(f'Deleted task {args.id}: {removed["description"]}')

def cmd_mark(args: argparse.Namespace) -> None:
    internal = args.status
    data = load_data()
    index = find_task_index(data["tasks"], args.id)
    data["tasks"][index]["status"] = internal
    save_data(data)
    print(f"Task {args.id} marked as {internal}.")

def _filter_tasks(tasks: list[dict[str, Any]], filter_name: str) -> list[dict[str, Any]]:
    if filter_name == "all":
        return tasks
    if filter_name == "completed":
        return [t for t in tasks if t["status"] == "completed"]
    if filter_name == "not completed":
        return [t for t in tasks if t["status"] != "completed"]
    if filter_name == "in-progress":
        return [t for t in tasks if t["status"] == "in-progress"]
    raise TaskCliError(
        f"Unknown list filter {filter_name!r}. Use: all, completed, not completed, or in-progress."
    )
    

def cmd_list(args: argparse.Namespace) -> None:
    data = load_data()
    filtered = args.filter or "all"
    subset = _filter_tasks(data["tasks"], filtered)
    if not subset:
        label = {"all": "tasks", "completed": "completed tasks", "not completed": "pending tasks", "in-progress": "in-progress tasks"}[filtered]
        print(f"No {label}.")
        return
    print(f"Tasks ({filtered}):")
    for t in sorted(subset, key=lambda x: x["id"]):
        print(f" [{t['id']}] {t['status']} {t['description']}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task management CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("description", nargs="+", help="Description of the task.")
    add_parser.set_defaults(func=cmd_add)

    update_parser = subparsers.add_parser("update", help="Update an existing task's description.")
    update_parser.add_argument("id", type=int, help="ID of the task to update.")
    update_parser.add_argument("description", nargs="+", help="New description of the task.")
    update_parser.set_defaults(func=cmd_update)

    delete_parser = subparsers.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("id", type=int, help="ID of the task to delete.")
    delete_parser.set_defaults(func=cmd_delete)

    mark_parser = subparsers.add_parser("mark", help="Mark a task's status.")
    mark_parser.add_argument("id", type=int, help="ID of the task to mark.")
    mark_parser.add_argument(
        "status",
        choices=["pending", "in-progress", "completed"],
        help="New status for the task.",
    )
    mark_parser.set_defaults(func=cmd_mark)

    list_parser = subparsers.add_parser("list", help="List tasks with optional filtering.")
    list_parser.add_argument(
        "--filter",
        choices=["all", "completed", "not completed", "in-progress"],
        default="all",
        help="Filter tasks by status.",
    )
    list_parser.set_defaults(func=cmd_list)

    return parser

def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    try:
        args.func(args)
    except TaskCliError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())