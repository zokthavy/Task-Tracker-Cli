# Task CLI

A simple command-line task management tool for organizing and tracking your tasks.

## Installation

Make sure you have Python 3.7+ installed. No additional dependencies are required.

## Usage

Run the program using:

```bash
python3 task-cli.py [command] [options]
```

## Commands

### Add a Task

Add a new task to your task list.

```bash
python3 task-cli.py add "Your task description"
```

**Example:**
```bash
python3 task-cli.py add "Buy groceries"
python3 task-cli.py add "Finish project report"
```

### List Tasks

Display all tasks or filter by status.

```bash
python3 task-cli.py list [--filter FILTER]
```

**Filter options:**
- `all` (default) - Show all tasks
- `pending` - Show only pending tasks
- `in-progress` - Show only in-progress tasks
- `completed` - Show only completed tasks

**Examples:**
```bash
python3 task-cli.py list                    # Show all tasks
python3 task-cli.py list --filter pending   # Show pending tasks
python3 task-cli.py list --filter completed # Show completed tasks
```

### Update a Task

Update the description of an existing task.

```bash
python3 task-cli.py update [ID] "New description"
```

**Example:**
```bash
python3 task-cli.py update 1 "Buy groceries and cook dinner"
```

### Mark a Task

Change the status of a task.

```bash
python3 task-cli.py mark [ID] [STATUS]
```

**Status options:**
- `pending` - Not yet started
- `in-progress` - Currently being worked on
- `completed` - Finished

**Examples:**
```bash
python3 task-cli.py mark 1 pending        # Mark task as pending
python3 task-cli.py mark 1 in-progress    # Mark task as in progress
python3 task-cli.py mark 1 completed      # Mark task as completed
```

### Delete a Task

Remove a task from your task list.

```bash
python3 task-cli.py delete [ID]
```

**Example:**
```bash
python3 task-cli.py delete 1
```

## Data Storage

Tasks are stored in a `tasks.json` file in the current directory. The file is automatically created the first time you add a task.

## Example Workflow

```bash
# Add some tasks
python3 task-cli.py add "Learn Python"
python3 task-cli.py add "Build a project"
python3 task-cli.py add "Read documentation"

# List all tasks
python3 task-cli.py list

# Start working on a task
python3 task-cli.py mark 1 in-progress

# Update a task description
python3 task-cli.py update 1 "Learn advanced Python"

# Mark a task as completed
python3 task-cli.py mark 1 completed

# List only pending tasks
python3 task-cli.py list --filter pending

# Delete a task
python3 task-cli.py delete 3
```

## Error Handling

The program validates all input and will display clear error messages if:
- You provide an empty task description
- You reference a non-existent task ID
- The tasks file is corrupted or invalid

All errors are prefixed with `Error:` for easy identification.
