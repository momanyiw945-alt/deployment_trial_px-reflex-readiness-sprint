### Setup (before you start talking)
- Browser open, three tabs/windows ready: Retailer view, Dispatcher view, Rider view — all pointed at https://deployment-trial-px-reflex-readiness.onrender.com
- Database reset to a clean state (no leftover test deliveries from earlier runs) — note: on Render free tier, a fresh redeploy naturally gives you a clean database (confirmed: /riders reseeds Brian, Kevin, James on every new deploy), so redeploying right before presenting is actually the easiest way to reset state
- **Important:** hit the live URL 2–3 minutes before you go on stage — free tier spins down after ~15 min idle, and the first request after that can take 50+ seconds to wake up. Don't let that happen live.
- Presenter for this section: **[Member ___]**

### Beat 1 — Retailer creates a delivery (~45 sec)
> "We'll follow one delivery through its full lifecycle. I'm a retailer — say, a hardware store — and I've just got an order to send out."

- Click into Retailer tab (`/retailer`)
- Fill form: Customer Name, Phone, Address, Item Description
- Submit — this hits `POST /deliveries`
- Point at result: "Delivery [D00X] is now logged, status **Pending**."

### Beat 2 — Dispatcher assigns a rider (~45 sec)
> "Now switching to the dispatcher — this is the person who sees every open request and decides who takes it."

- Switch to Dispatcher tab (`/dispatcher`)
- Point at the open delivery in the list
- Click assign, select a rider — this hits `POST /deliveries/<id>/assign`
- Point at result: "Status is now **Assigned**, and it's tied to [Rider name]."

### Beat 3 — Rider updates status (~60 sec)
> "Now the rider's view — they only see what's assigned to them, and they can't skip steps."

- Switch to Rider tab (`/rider`)
- Show delivery appears with status Assigned
- Click "Picked Up" → status updates via `PATCH /deliveries/<id>/status`
- Click "Delivered" → status updates again
- **Optional but strong:** try clicking a disabled/invalid transition (e.g. attempt to jump straight to Delivered from Assigned) to show the guard actively works — the server rejects this with a 409 and a clear error message ("Invalid transition: cannot move from X to Y"), not just a disabled button in the UI. This is worth calling out explicitly: the validation lives in the API itself, so it can't be bypassed by calling the endpoints directly.

### Beat 4 — Retailer sees it close the loop (~30 sec)
> "And back to the retailer — no phone call, no WhatsApp message needed. They see it went from Pending to Delivered on their own screen."

- Switch back to Retailer tab, refresh/poll
- Point at final status: **Delivered**

### Closing line (~15 sec)
> "That's the full loop — Retailer, Dispatcher, Rider, no manual coordination outside the app. It's also live on the public internet right now, not running on someone's laptop — happy to take questions."

---

**Backup plan if something breaks live:** [name which member has a phone-recorded backup video of a clean run]. One known fragile point worth having top of mind: the free-tier spin-down delay (Trade-off 6 in the log) — if the app is slow to respond because it wasn't warmed up, that's a known, already-documented trade-off, not a surprise failure. Say so plainly if it happens rather than looking flustered.---

**Backup plan if something breaks live:** name which member has a phone-recorded backup video of a clean run, and where the trade-off log's "known fragile points" list overlaps with anything that might break — if the panel sees it break, you want to already have that failure listed as a known trade-off, not a surprise.

---

## Part 2: State → Context → Evidence Prep

**[DRAFT — every row below is a starting point, not a final answer. Each owner: read your row, rewrite it in your own words, and only keep evidence you can personally defend if pushed on it. Delete anything you can't back up.]**

### Category 1 — Architecture ("why this choice over the obvious alternative?")

| Likely question | Owner | State → Context → Evidence (draft) |
|---|---|---|
| Why Flask instead of Node/Django/etc.? | Member 4 | **State:** We chose Flask because it's the smallest framework that still gives us real routing and JSON handling. **Context:** Django bundles an ORM, admin panel, and auth system we didn't need for a 4-endpoint API — that's more surface area to explain under questioning, not less. Node would have meant splitting the team's Python skillset across two languages mid-sprint. **Evidence:** Our entire backend is one file, `app.py`, at 139 lines — every team member can read the whole API in under 5 minutes. |
| Why SQLite instead of Postgres/MySQL? | Member 4 | **State:** SQLite for the sprint because it needs zero setup — no server to run, no connection string, no separate service to keep alive. **Context:** The brief's grading focus is the request → assign → status workflow, not infrastructure — spending Day 1 configuring a database server would have traded build time for something not being graded. **Evidence:** We deployed to Render with zero database configuration — `pip install -r requirements.txt` and the app creates and seeds its own database file on first run, confirmed live after a fresh deploy. |
| Why did you split retailer/dispatcher/rider into separate views instead of one shared dashboard? | Member 1/2/3 | **State:** Separate views because each persona only needs a fraction of the total information, and mixing them risks a dispatcher seeing (or accidentally acting on) something meant for a rider. **Context:** The case study frames these as three distinct jobs with different responsibilities — a single dashboard would mean building permission logic to hide/show sections, which is more complex than just building three focused pages. **Evidence:** [fill in — e.g. "each template is under X lines and only calls the endpoints that persona actually needs"] |
| Why REST instead of GraphQL or something else? | Member 4 | **State:** Plain REST because our data shape is simple and fixed — a handful of resources (deliveries, riders) with predictable fields, not a flexible query surface clients need to shape themselves. **Context:** GraphQL's main advantage is letting clients request exactly the fields they need across nested relationships — we don't have deep nesting, and adding a GraphQL layer would be new infrastructure to justify for no real benefit here. **Evidence:** The entire "frozen API contract" is 6 routes, documented in one table in our README — anyone on the team can recite it. |

### Category 2 — Trade-offs ("what did you simplify, and what's the cost?")

| Likely question | Owner | State → Context → Evidence (draft) |
|---|---|---|
| Why no real authentication? | Member 1 | **State:** There's no login — you pick which persona/rider you are from a dropdown. **Context:** The brief's core problem is delivery visibility, not access control, and building real role-based auth (sessions, password handling, permission checks) would have taken time directly away from the workflow being graded. **Evidence:** See Trade-off 1 in the trade-off log — this was a deliberate, named decision, not an oversight. |
| Why no GPS/live location tracking? | Member 3 | **State:** We show status (Assigned/Picked Up/Delivered), not live position. **Context:** The brief explicitly frames GPS as something to consider, not something core — status visibility already answers "where does this delivery stand," which is the actual problem stated in the brief. **Evidence:** See Trade-off 2 in the trade-off log. |
| Why no QR/barcode scanning for order confirmation, given the case study mentions it? | Lastborn | **State:** A rider confirms delivery with a single button tap instead of scanning a code. **Context:** Real scanning needs camera access, a barcode library, and generating a unique code per delivery — meaningful build time for something that doesn't change the core architecture being tested. **Evidence:** See Trade-off 5 in the trade-off log — we prioritized proving the full request→assign→status loop works over adding a verification layer on top of it. |
| Why polling instead of WebSockets/real-time sync, and how do you handle a rider going offline mid-update? | Member 4 | **State:** Every screen polls the server every 3 seconds rather than the server pushing updates instantly, and if a status update fails to send, it simply fails — there's no retry. **Context:** Polling is far simpler to build and reason about, and a 3-second delay is invisible in a live demo. Full offline handling (local caching, retry queues) is production-hardening we didn't have time to add. **Evidence:** See Trade-off 3 in the trade-off log. |
| Why no rider notification when assigned? | Member 2 | **State:** A rider only sees a new assignment when they check their own dashboard or the next poll cycle refreshes it — nothing pushes to them. **Context:** Push notifications require infrastructure (SMS gateway or push service) that's out of scope for demonstrating the core workflow. **Evidence:** See Trade-off 4 in the trade-off log. |

### Category 3 — Edge cases ("what happens when two things happen at once, or something fails partway through?")

| Likely question | Owner | State → Context → Evidence (draft) |
|---|---|---|
| What if a dispatcher tries to assign a delivery that's already assigned? | Member 4 | **State:** The server rejects it. **Context:** The assign endpoint checks the delivery's current status before allowing assignment — it only proceeds if the delivery is still `PENDING`. **Evidence:** In `app.py`, `assign_delivery` returns a 409 error ("Cannot assign a delivery with status X") if the status isn't `PENDING` — this is enforced server-side, confirmed by reading the actual route code. |
| What if a rider tries to skip a status (Assigned → Delivered directly)? | Member 3/4 | **State:** The server rejects it. **Context:** Status can only move to the single next step in a fixed order — `PENDING → ASSIGNED → PICKED_UP → DELIVERED` — the server computes what the "expected next" status is and compares it against what was requested. **Evidence:** `update_status` in `app.py` returns a 409 with the message "Invalid transition... Next valid status is X" if you try to skip — this is the guard we demoed live in Beat 3. |
| What if two dispatchers try to assign the same delivery at the same moment? | Member 4 | **State:** [fill in — this is a genuine edge case worth testing before the panel, not just reasoning about] Likely: whichever request reaches the database first wins, and the second request would then fail the "already assigned" check above, since the status would no longer be PENDING by the time it's checked. **Context:** SQLite processes writes one at a time, so true simultaneous writes can't both "win" — but we haven't specifically load-tested this race condition. **Evidence:** [fill in — worth actually trying this with two browser tabs clicking assign on the same delivery at nearly the same time before the panel, so this becomes a tested answer, not a guessed one] |
| What happens if the server restarts mid-delivery — is data lost? | Member 4 | **State:** Any delivery data that hasn't been written to a persistent disk is lost, because we're on Render's free tier where the filesystem resets on restart. **Context:** This is the tradeoff we documented after actually deploying — we confirmed it directly by checking `/riders` after a fresh deploy and seeing the database re-seed from scratch rather than showing leftover data. **Evidence:** See Trade-off 6 in the trade-off log — this isn't hypothetical, it's something we observed happen. |
| What if the retailer submits a form with missing/invalid data? | Member 1 | **State:** The server rejects it with a clear error listing which fields are missing. **Context:** `create_delivery` in `app.py` checks that customerName, phone, address, and itemDescription are all present before creating the record — it doesn't silently accept a partial delivery. **Evidence:** The route returns a 400 with "Missing required fields: X, Y" — this validation happens server-side, so it can't be bypassed by a broken or missing frontend check. |

### Category 4 — Candor ("a question with no clean answer, to see if you bluff")

Rehearse saying this sentence out loud until it's automatic: **"I don't know, but here's how I'd find out: [...]"**

| Likely question | Owner | Honest answer + "how I'd find out" (draft) |
|---|---|---|
| How would this scale to 10,000 deliveries a day? | Member 4 | I don't know our actual breaking point — we haven't load-tested this build. Here's how I'd find out: run a load-testing tool (like Locust or k6) against the deployed API to find where response times degrade, starting with the biggest known constraint — SQLite doesn't handle concurrent writers well, so that's almost certainly the first thing to break, well before 10,000/day. |
| How would you prevent a rider from marking something Delivered fraudulently (no proof of delivery)? | Member 3 | Honestly, right now nothing stops that — a rider can tap "Delivered" with no verification at all. Here's how I'd find out/fix it: this is exactly what Trade-off 5 (QR scanning) would solve — requiring a scan tied to the specific delivery at the point of drop-off would mean the status can't flip without physical proof of presence. |
| What's your plan for offline riders with no signal? | Member 3/5 | I don't have a real plan for this today — the app assumes a live connection for every status update, and there's no local queue if that connection drops. Here's how I'd find out/fix it: this is Trade-off 3 in the log — I'd look at a local-first pattern (e.g. writing the status change to local storage immediately, then syncing to the server once connectivity returns), similar to how offline-capable mobile apps handle intermittent connectivity. |
| How would you handle multiple retailers/regions at once? | Member 5 | The current data model doesn't separate deliveries by retailer or region at all — every delivery and rider is in one shared pool. Here's how I'd find out/fix it: I'd need to add a `retailerId` (and possibly `region`) field to the data model, then filter every query by it — this is a real schema change, not just a UI change, so I'd want to scope how much of the current API contract would need to change before committing to a timeline. |
---

## Handoff Assignments (fill in before Day 2 mock panel)

| Slide | Owner | Fields first question in |
|---|---|---|
| Problem | Member 5 (suggested — owns the narrative docs) | Architecture |
| Solution | Member 5 (suggested) | Trade-offs |
| Architecture | Member 4 (suggested — owns app.py/models.py) | Edge cases |
| Trade-offs | Rotates across whoever's trade-off is up (suggested) | Candor |
| Demo | Rotates — whoever isn't driving the keyboard | (rotates) |
| Roadmap | Member 5 (suggested) | (rotates) |

**Rule:** every member must field at least one live question. If your name is only on one row above, you're also on standby to jump in on a category if the assigned person freezes.

*(This is a starting proposal based on existing file ownership — confirm/reassign as a group during Day 2's handoff rehearsal, not unilaterally.)*
