# Implementation Plan — Kanban with Comments & @Mentions

Built on the existing FastAPI + SQLModel + JWT starter. Each step is TDD: write the
failing test first, run it, see it fail, then implement. Commit `test:` then `feat:`.
Total estimate: ~4.5 hrs of build (fits the 90-min TDD budget if UI is kept thin).

Legend: **[RISK]** = flagged risky by the planning pass; do these carefully / early.

---

### Step 1 — Data models: Board, Column, Card (30 min)
Add `Board`, `Column`, `Card` SQLModel table models + request/response schemas in
`app/models.py`. Board belongs to a user; Column belongs to a Board; Card belongs to a
Column. Import them so `metadata.create_all` sees them.
- **Depends on:** nothing (starter models already exist).
- **Note:** follow the existing `Task` model's `user_id` + `Optional[int]` id pattern exactly.

### Step 2 — Board CRUD with ownership authz (25 min)
`app/boards.py` router: create/list/rename/delete. Every route takes
`user = Depends(get_current_user)` and filters by `user.id`; non-owned rows return 404.
- **Depends on:** Step 1.
- **TDD target (required):** board CRUD authorization — "I can only mutate my own boards."

### Step 3 — Default column seed on board creation (15 min)
Creating a board seeds three columns: "Todo", "Doing", "Done" with `order` 0/1/2.
- **Depends on:** Steps 1-2.

### Step 4 — Column CRUD + reorder (30 min) **[RISK]**
Add/rename/delete columns; reorder via an `order` integer. Reorder must persist to DB.
- **Depends on:** Steps 1-3.
- **Why risky:** reordering semantics (contiguous vs sparse `order` values, what happens
  on delete) are easy to get subtly wrong. Decide the ordering scheme up front.

### Step 5 — Card CRUD + move between columns (30 min) **[RISK]**
Create/edit/delete cards; move a card by updating its `column_id`. Ownership enforced
transitively (card -> column -> board -> user).
- **Depends on:** Steps 1-4.
- **Why risky:** the ownership check is now two joins deep. Getting the 404-vs-leak
  boundary right (don't reveal other users' cards) is the correctness crux.
- **TDD target (required):** card CRUD authorization.

### Step 6 — Mention parser (25 min) **[RISK]**
Pure function: given comment body text, return the list of valid `@username` mentions.
Regex to extract tokens + a user lookup to keep only real users.
- **Depends on:** nothing (pure logic) — can be built in parallel early.
- **Why risky:** regex edge cases (email addresses, `@` mid-word, punctuation, duplicate
  mentions, unknown users). This is the single most test-worthy unit — cover it heavily.
- **TDD target (required):** mention parsing (regex + user lookup).

### Step 7 — Comments on cards (20 min)
`Comment` model + POST `/cards/{id}/comments` and list. One level deep, no nesting.
- **Depends on:** Steps 5, 6.

### Step 8 — Notification creation on mention (25 min) **[RISK]**
When a comment is posted, run the parser; for each valid mentioned user create a
`Notification` row. This is the state-flow the whole feature hinges on.
- **Depends on:** Steps 6, 7.
- **Why risky:** ordering (save comment, THEN parse, THEN notify) and not double-notifying
  on edit. Beginner track: mentioning yourself should still create a notification.
- **TDD target (required):** notification creation.

### Step 9 — Notifications feed + mark-read (20 min)
GET `/notifications` (unread first, chronological), PATCH to mark read on click,
and an unread-count endpoint for the nav badge.
- **Depends on:** Step 8.

### Step 10 — Minimal UI wiring (40 min)
Thin templates/pages for board view, card detail w/ comments, notifications feed, and a
nav bar with the unread badge. Drag-drop persists `column_id` via the API.
- **Depends on:** Steps 2-9.
- **Note:** cut here first if over budget — the workflow artifacts matter more than polish.

### Step 11 — Full suite green + screenshots (15 min)
Run `pytest`, confirm all unit + integration tests pass, capture terminal + UI screenshots
for the report.
- **Depends on:** all above.

---

## Dependency summary
- Backbone chain: 1 → 2 → 3 → 4 → 5 → 7 → 8 → 9.
- Step 6 (mention parser) is independent — build it early to de-risk Step 8.
- Step 10 (UI) depends on the API being done; Step 11 gates the report.

## Riskiest steps (do early / test hardest)
1. **Step 6 — mention parser:** most edge cases, cheapest to test in isolation.
2. **Step 8 — notification creation:** the core state flow; ordering bugs hide here.
3. **Step 5 — card move + transitive ownership:** where a real authz leak could occur.
4. **Step 4 — column reorder:** persistence + ordering scheme is subtly fiddly.
