WRITE_TODOS_DESCRIPTION = """Create or replace the agent's structured task list for multi-step work.

## When to Use
- Multi-step workflows (gather evidence → synthesize → deliver a report)
- Coordinated steps across specialists or multiple searches
- User or coordinator explicitly requests a plan or task breakdown

## When NOT to Use
- Greetings, casual chat, or simple Q&A
- Single-step actions (one search, one answer)
- Trivial requests with an obvious single action

## Structure
- Each call replaces the entire todo list (not a partial update)
- Each todo has `content` (str) and `status` (`pending`, `in_progress`, or `completed`)
- Use clear, actionable step descriptions

## Best Practices
- Only one `in_progress` task at a time
- Mark `completed` as soon as a step is fully done
- For the coordinator, include a final step to save and present the user-facing report when appropriate
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


SAVE_REPORT_DESCRIPTION = """Save or replace a named report in agent state.

## When to Use
- After a specialist returns a final answer that should be persisted
- After producing a risk assessment that later steps may need
- Before presenting a report to the user

## Canonical names
- `product_dossier` — product supply-chain context
- `news_brief` — disruption / news compilation
- `risk_assessment` — scored supply-chain risks
- `mitigation_plan` — root-cause mitigations

## Behavior
Upserts by `name` (replaces prior content for that name)."""


READ_REPORT_DESCRIPTION = """Read a saved report from agent state.

## When to Use
- To ground further work on a previously saved product dossier, news brief, or risk assessment
- To inspect what reports already exist before continuing

## Arguments
- `name` (optional): specific report to load. Omit to list all saved reports with short previews.

## Returns
Full report content, a listing of saved reports, or an error if the name is missing."""


PRESENT_REPORT_DESCRIPTION = """Present a saved report to the user.

## When to Use
- When the deliverable that answers the user's request is ready
- After saving the final artifact (`product_dossier`, `news_brief`, `risk_assessment`, or `mitigation_plan`)

## Behavior
Copies the named report from `reports` into `presented_files`. Fails if the report was not saved first.

## When NOT to Use
- For intermediate drafts the user did not ask to see
- Before the report exists in state"""


KNOWLEDGE_SEARCH_DESCRIPTION = """Search the product / supply-chain knowledge base.

## When to Use
- To retrieve demand, sourcing, manufacturing, delivery, materials, plants, warehouses, and related entities for a product
- To verify alternate sites, capacity, stock, export controls, or local rules

## Returns
Relevant document chunks with metadata such as product, source, and section headers."""


NEWS_SEARCH_DESCRIPTION = """Search the disruption / news corpus.

## When to Use
- To find events linked to product entities (materials, locations, plants, warehouses)
- To gather event type, timing, and estimated impact for risk or mitigation work

## Returns
Relevant news chunks with metadata such as event_id, published_date, event_type, and entities."""


ASSESS_RISKS_DESCRIPTION = """Calculate risk scores from rubric factors. Use this tool whenever you need any numeric risk score or an overall risk score. Do NOT compute or guess the numbers yourself.

## When to Use
- Supply-chain risk analysis requested by the user
- Once product and news evidence has been gathered (product_dossier / news_brief)
- To obtain the accurate score for each distinct risk and the cumulative risk across all of them

## When NOT to Use
- Simple Q&A about products or news without scoring
- Mitigation planning before a scored risk assessment exists

## Input
Pass EVERY distinct risk in the assessment in ONE call as a list of items. Each item needs:
- `risk_id`: stable id, e.g. R1, R2
- `product`: product that is at risk
- `stage`: Demand | Sourcing | Manufacturing | Delivery
- `dimension`: the part of the chain hit (material, plant, warehouse, location, policy, labor, logistics, ...)
- `severity` (S), `exposure` (E), `fragility` (F): each an integer 1–5, derived strictly from gathered evidence

## Computed output (deterministic arithmetic)
- Per-risk Score = round((S x E x F) / 12.5), clamped to 1–10, with band (1–3 Low, 4–6 Moderate, 7–8 High, 9–10 Critical)
- Cumulative risk = round(RMS of every individual score), clamped to 1–10, same bands. The root mean square combines each score while giving higher risks more weight.

Use the returned numbers verbatim in your `risk_assessment` report; never alter them."""
