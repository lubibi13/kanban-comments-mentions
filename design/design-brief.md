# Design Brief — Kanban with Comments & @Mentions

Single-user Kanban board. A signed-in user organizes cards across columns, comments on
cards, and gets notified when a comment @-mentions them. Beginner track: the mentioned
user is the signed-in user themselves (via a seeded second user or a second browser).

---

## 1. Wireframes

### 1a. Board view — `/boards/{id}`

```
+--------------------------------------------------------------------------+
|  Kanban            Boards   Notifications (3)          nico@example.com   |
+--------------------------------------------------------------------------+
|  My First Board                              [ Rename ]  [ Delete ]        |
+--------------------------------------------------------------------------+
|                                                                          |
|   Todo            +      Doing           +      Done            +         |
|  +-------------+        +-------------+        +-------------+            |
|  | Card: Wire  |        | Card: Auth  |        | Card: Setup |            |
|  | up nav bar  |        | endpoints   |        | repo        |            |
|  | @nico       |        |             |        |             |            |
|  +-------------+        +-------------+        +-------------+            |
|  | Card: Seed  |        + Add card    |        + Add card    |            |
|  | columns     |        +-------------+        +-------------+            |
|  +-------------+                                                          |
|  + Add card    |                                                          |
|  +-------------+                                                          |
|                                                                          |
|  [ + Add column ]                                                        |
+--------------------------------------------------------------------------+

- Columns render left-to-right in `order` sequence.
- Cards draggable within/between columns; drop persists new column_id to the API.
- Column headers editable inline (rename); drag handle on header to reorder columns.
- Clicking a card opens the Card Detail view (modal or route).
```

### 1b. Card detail / comment view — `/boards/{id}/cards/{cardId}`

```
+---------------------------------------------------+
|  Wire up nav bar                            [ x ]  |
+---------------------------------------------------+
|  Column: [ Todo v ]        Assignee: [ nico v ]    |
|                                                    |
|  Description                                       |
|  +---------------------------------------------+   |
|  | Needs unread count badge on every page.     |   |
|  +---------------------------------------------+   |
|                                                    |
|  Comments (2)                                      |
|  ------------------------------------------------  |
|  nico  ·  2h ago                                   |
|  Looks good. cc @nico to double-check the badge.   |
|         ^^^^^ rendered as link -> /users/nico      |
|  ------------------------------------------------  |
|  nico  ·  just now                                 |
|  On it.                                            |
|  ------------------------------------------------  |
|  [ Write a comment...  type @ to mention ]  [Post] |
+---------------------------------------------------+

- @username tokens in a saved comment render as links to /users/{username}.
- Posting a comment with @mention creates a Notification row for the mentioned user.
```

### 1c. Notifications feed — `/notifications`

```
+--------------------------------------------------------------+
|  Notifications                              [ Mark all read ] |
+--------------------------------------------------------------+
|  UNREAD                                                       |
|  * nico mentioned you in "Wire up nav bar"      2h ago        |
|      -> click: marks read + opens the card                   |
|  * nico mentioned you in "Auth endpoints"       5h ago        |
|  ------------------------------------------------------------ |
|  EARLIER                                                      |
|    nico mentioned you in "Setup repo"          yesterday      |
+--------------------------------------------------------------+

- Unread listed first, then read, each group in reverse-chronological order.
- Clicking a notification marks it read and navigates to the source card.
- Nav-bar unread count reflects count of is_read = false.
```

---

## 2. Component list

| Component | Props | Responsibility |
|---|---|---|
| `NavBar` | `unreadCount` | Global nav; shows Boards / Notifications links and live unread badge on every page. |
| `BoardList` | `boards[]` | Renders the user's boards at `/boards`; create/rename/delete entry points. |
| `Board` | `board`, `columns[]`, `cards[]` | Board view; lays columns out by `order`; owns drag-and-drop state. |
| `Column` | `column`, `cards[]`, `onRename`, `onDelete`, `onReorder` | One column; inline rename, add-card, drag handle for column reorder. |
| `Card` | `card`, `onOpen`, `onDragEnd` | Card tile in a column; drag source; click opens detail. |
| `CardDetail` | `card`, `comments[]`, `onPost`, `onMove` | Modal/route for a single card; edit fields, move column, comment thread. |
| `CommentList` | `comments[]` | Renders comments newest-last with author + timestamp. |
| `Comment` | `comment` | Single comment; renders body with `MentionText`. |
| `MentionText` | `body` | Parses `@username` tokens and renders each as a link to `/users/{username}`. |
| `CommentForm` | `onSubmit` | Compose box; submits comment body to the API. |
| `NotificationsFeed` | `notifications[]`, `onRead` | `/notifications` list; unread-first grouping; click marks read + navigates. |

---

## 3. User flows

### Flow A — Create a card
1. User is on `/boards/{id}`.
2. Clicks **+ Add card** under a column.
3. Enters a title (required); optional description.
4. Client POSTs `/cards` with `column_id`, `title`.
5. API creates the card scoped to the user; returns it.
6. New card tile appears at the bottom of that column.

### Flow B — Add a comment with an @mention
1. User opens a card (`CardDetail`).
2. Types a comment: `Nice work @nico`.
3. Clicks **Post** → client POSTs `/cards/{id}/comments` with the raw body.
4. API saves the comment, then parses `@username` tokens.
5. For each matched, existing user, the API creates a `Notification` row (type = mention).
6. `MentionText` renders `@nico` as a link to `/users/nico`.
7. The mentioned user's nav-bar unread count increments.

### Flow C — Mentioned user sees and clicks a notification
1. Mentioned user (or same user, second browser) loads any page.
2. Nav bar shows an unread count badge.
3. Clicks **Notifications** → `/notifications`, unread listed first.
4. Clicks a notification → API marks it `is_read = true`; client navigates to the source card.
5. Unread count decrements; the item moves out of the UNREAD group on next load.

---

## Notes
- No design tool used; ASCII wireframes are the intended fidelity per the assignment.
- The nav-bar unread count is the one piece of shared state across every page —
  worth a single lightweight fetch on navigation rather than per-component polling.
