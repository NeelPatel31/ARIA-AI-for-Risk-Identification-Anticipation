WRITE_TODOS_DESCRIPTION = """Create or replace the agent's structured task list for multi-step file work.

## When to Use
- Multi-step file workflows (inspect → modify → deliver via `/output` + `present_files`)
- Multiple coordinated file operations
- User explicitly requests a plan or task breakdown

## When NOT to Use
- Greetings, casual chat, or simple Q&A
- Single-step actions (one file view, one edit, one answer)
- Trivial requests with an obvious single action

## Structure
- Each call replaces the entire todo list (not a partial update)
- Each todo has `content` (str) and `status` (`pending`, `in_progress`, or `completed`)
- Use clear, actionable step descriptions

## Best Practices
- Only one `in_progress` task at a time
- Mark `completed` as soon as a step is fully done
- Include a final step to save deliverables to `/output` and call `present_files` when sharing with the user
- Prune irrelevant items to keep the list focused

## Progress Updates
- Call `write_todos` again to change status or edit content
- Reflect real-time progress; do not batch completions
- If blocked, keep the task `in_progress` and add a new todo describing the blocker"""


READ_TODOS_DESCRIPTION = """Read the current todo list from agent state.

## When to Use
- After completing a step in a multi-step workflow to see what remains
- When re-orienting mid-task before deciding the next action

## When NOT to Use
- For simple requests that never needed a todo list
- When you already know the remaining steps without checking

## Returns
A formatted summary of all todos with status, or a message if the list is empty."""