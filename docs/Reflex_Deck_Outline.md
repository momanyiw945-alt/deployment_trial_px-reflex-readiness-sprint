# Reflex — Presentation Deck Outline
Structure required by the brief: Problem → Solution → Architecture → Trade-offs → Roadmap, one takeaway per slide. Filled in below where the content is already known from the case study; bracketed items need the real Day 1 build details before finalizing on Day 2.

**Target: ~10 minutes total. Roughly 80–90 seconds per slide across 7 slides.**

---

## Slide 1 — Problem
**One takeaway:** Small retailers have no visibility into their own deliveries.

**Content:**
- Small Kenyan retailers — electronics shops, pharmacies, hardware stores — coordinate deliveries over WhatsApp and phone calls.
- No record of who's assigned, no status visibility, no proof of delivery.
- The cost of this: a retailer has no way to answer "where is my customer's order right now" without manually calling the rider — every status check is a phone call, and there's no record afterward of who confirmed what, or when.

**Visual suggestion:** A simple before/after: messy WhatsApp thread vs. a clean status view.

---

## Slide 2 — Solution
**One takeaway:** Reflex gives every delivery a clear owner and a visible status at every stage.

**Content:**
- Reflex: a system where a retailer logs a delivery, a dispatcher assigns it to a rider, and the rider updates its status — so the retailer always knows where it stands.
- Flow: Request → Assign → Pick Up → Deliver

**Visual suggestion:** The four-step flow as a simple horizontal diagram.

---

## Slide 3 — How Reflex Works
**One takeaway:** Three roles, three focused screens, one shared source of truth.

**Content:**
- 🏪 Retailer — creates the delivery request
- 🧑‍💼 Dispatcher — sees open requests, assigns a rider
- 🛵 Rider — sees assigned deliveries, updates status through Assigned → Picked Up → Delivered

**Visual suggestion:** Three persona icons with one-line job descriptions (already used on the app's own home page — reuse it).

---

## Slide 4 — Architecture
**One takeaway:** We kept the stack deliberately simple so every member can defend every layer.

**Content:**

Browser (Retailer / Dispatcher / Rider views)
↓
Flask (routes + REST API, single app.py)
↓
SQLite (single reflex.db file)
↓
Deployed on Render — gunicorn serving the Flask app,
free-tier web service

- Frontend: plain HTML/CSS/JS via Jinja templates — no build step, no frontend framework, deliberately, so the whole team can read and explain every file (direct from our own README, and a real defensible choice, not just a limitation).
- Backend: Flask
- Database: SQLite
- API: REST — create, list, and fetch deliveries; list riders; assign a rider to a delivery; and move a delivery forward exactly one status step (server-side enforced, so the API itself can't be used to skip a step even if someone bypasses the UI).
- Deployment: Render web service, built via `pip install -r requirements.txt`, started via `gunicorn app:app`.

**Anticipate:** "Why this choice over the obvious alternative?" — see the Architecture section of the S→C→E prep doc for the rehearsed answer.

---

## Slide 5 — Demo
**One takeaway:** The full loop actually works, live, end to end.

**Content:** No text-heavy slide here — this is where you switch to the live app and run the demo script (see `Reflex_Demo_Script_and_SCE_Prep.md`).

**Live URL:** https://deployment-trial-px-reflex-readiness.onrender.com

**Backup plan line to have ready:** [name who has a backup recording, in case live demo breaks — note: free-tier Render spins down after ~15 min idle, so if the app hasn't been hit recently, the first request can take 50+ seconds to wake up. Hit the URL once a minute or two before presenting to "warm it up," and have the backup recording ready regardless.]

---

## Slide 6 — Trade-offs
**One takeaway:** We know exactly where this system is weak, and why we accepted it anyway.

**Content:** Pull directly from the finalized `Reflex_TradeOff_Log.md` — do not re-write it differently here, use the exact same trade-offs so your slide and your written log agree with each other under questioning.

1. No real authentication — views are open, "becoming" a persona is just a dropdown
2. No GPS / live location tracking during transit
3. Polling every 3 seconds instead of real-time sync, with no offline retry
4. No notification when a delivery is assigned — rider only sees it on next check/poll
5. No QR/barcode scanning for order confirmation — single button tap instead
6. SQLite on ephemeral storage — data resets on every redeploy/restart (confirmed live: `/riders` reseeds Brian, Kevin, James fresh on every new deploy)

*(Brief requires a minimum of 3 on the slide — showing all 6 briefly signals we found our own weak points rather than getting caught off guard, per the rubric's "Defense & Cross-Exam" row.)*

---

## Slide 7 — Roadmap
**One takeaway:** We know what's next, in priority order.

**Content:**

Now
Full request → assign → pick up → deliver loop works end to end,
deployed and reachable publicly, server-side status validation
enforced on every API call, not just hidden in the UI.

Next
Real role-based authentication per persona
Move to a managed Postgres database for persistence
WebSockets/SSE instead of polling, with retry on failed status updates

Later
GPS/live location tracking during transit
Push/SMS notifications on assignment
QR/barcode scanning for delivery confirmation


---

## Slide-ownership placeholder (finalize on Day 2, also recorded in the S→C→E prep doc)

| Slide | Owner | Fields first question in |
|---|---|---|
| 1. Problem | | Architecture |
| 2. Solution | | Trade-offs |
| 3. How Reflex Works | | Edge cases |
| 4. Architecture | | Candor |
| 5. Demo | | (rotates) |
| 6. Trade-offs | | (rotates) |
| 7. Roadmap | | (rotates) |

**Reminder from the rubric:** every slide should land exactly one takeaway — if a slide is doing two jobs, split it. A non-technical stakeholder should be able to follow the whole story without needing the demo to make sense of the earlier slides.
