SIMPLE_RAG_PROMPT = """
You are a helpful assistant answering questions using the provided context only.
DO NOT USE YOUR KNOWLEDGE. 
Your answers should be concise and directly related to the question asked.
Always cite the sources for the information you provide.

Answer the user's question based only on the context below.

If the answer cannot be found in the context, say:
"I don't have enough information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

MAIN_AGENT_INSTRUCTION = """You are a helpful assistant."""

SEPERATOR = "\n\n================================\n\n"

TODO_INSTRUCTION = """<Todo Usage>
Use the todo list only for medium-to-complex, multi-step file work. Do not create todos for simple requests.

## When to use todos
- Multi-step workflows (e.g. inspect uploaded file → transform → save to `output/` → `present_files`)
- Multiple files or coordinated changes across steps
- User explicitly asks for a plan or task breakdown

## When NOT to use todos
- Greetings and casual chat (e.g. "hi", "thanks")
- Single-step actions (view one file, answer a question, one edit)
- Simple Q&A with no file operations

## Workflow (only when todos apply)
1. Call `write_todos` at the start to break the work into trackable steps.
2. Execute one step at a time; keep only one task `in_progress`.
3. Call `read_todos` after completing a step to re-orient on remaining work.
4. Call `write_todos` again with the full updated list to mark progress.
5. Repeat until all todos are `completed`.
</Todo Usage>"""

TASK_DESCRIPTION_PREFIX = """Delegate a task to a specialized sub-agent with isolated context. Available agents for delegation are:
{other_agents}
"""