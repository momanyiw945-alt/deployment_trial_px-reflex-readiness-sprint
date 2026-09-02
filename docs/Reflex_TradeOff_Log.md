# Reflex — Trade-Off Log
**Required by the brief as its own one-page deliverable — at least 3 weak points, each with an "acceptable because…" justification. This must match what's said on the Trade-offs slide, word-for-word in substance if not in phrasing.**

Fill in the bracketed sections once Day 1's build is final. The five candidates below are already identified from earlier planning and team discussion — confirm each still holds after the real build, add any new ones the mock panel or dry runs surface, and don't submit fewer than three.

---

### Trade-off 1 — Simplified authentication
**Owner:** Member 1 (with Member 3)

**What it is:** [e.g. "There's no real login — the retailer, dispatcher, and rider views are open, and 'becoming' a specific rider on the rider screen is just a dropdown, not an authenticated session."]

**Acceptable because:** [e.g. "The core problem we were asked to solve is delivery visibility, not access control. Building real role-based auth would have taken time away from the actual workflow the brief is graded on."]

**What we'd do with more time:** [e.g. "Implement proper role-based authentication so each persona only sees and can act on their own data, with a real login step per user."]

---

### Trade-off 2 — No GPS / live location tracking
**Owner:** Member 3

**What it is:** [e.g. "A rider's location isn't tracked during transit — the retailer and dispatcher can't see where the delivery physically is between Assigned and Delivered."]

**Acceptable because:** [e.g. "The brief's core problem is status visibility, not live navigation. GPS integration is also explicitly called out in the brief as something we could consider but shouldn't let derail the core workflow."]

**What we'd do with more time:** [e.g. "Add GPS tracking during transit so the retailer can see the rider's live position, not just a status label."]

---

### Trade-off 3 — Polling instead of real-time sync, with no offline handling
**Owner:** Member 4 (with Members 1, 2, 3)

**What it is:** [e.g. "Every screen refreshes its data every 3 seconds via polling (fetch on an interval), rather than the server pushing updates the instant something changes. There's also no queuing or retry if a rider's status update fails to reach the server due to no connection — it simply fails."]

**Acceptable because:** [e.g. "Polling is far simpler to build and reason about than WebSockets, and a 3-second delay is invisible in a live demo while still meeting the 'always know where a delivery stands' requirement from the brief. Full offline support (local caching, retry logic) is production-hardening, not core to proving the request → assignment → status flow this week."]

**What we'd do with more time:** [e.g. "Move to WebSockets or Server-Sent Events for instant updates instead of a 3-second delay, and add local caching + auto-retry on the rider's screen so a status update isn't lost if their connection drops."]

---

### Trade-off 4 — No notification when a delivery is assigned
**Owner:** Member 2

**What it is:** [e.g. "When a dispatcher assigns a delivery to a rider, the rider isn't proactively notified — they only see it once they check their own dashboard (or the next poll cycle refreshes it)."]

**Acceptable because:** [e.g. "Push notifications require infrastructure (SMS gateway, push service) that's out of scope for demonstrating the core workflow, and the brief explicitly lists notifications under 'don't overbuild it.'"]

**What we'd do with more time:** [e.g. "Add SMS or push notifications so a rider is alerted the moment they're assigned a delivery."]

---

### Trade-off 5 — No QR/barcode scanning for order confirmation
**Owner:** [assign — Lastborn, since he raised it]

**What it is:** [e.g. "A rider confirms delivery with a single button tap ('Delivered'), rather than scanning a QR/barcode tied to that specific order. The case study explicitly mentions 'scanning for order confirmation' as a capability the system supports."]

**Acceptable because:** [e.g. "Real scanning needs camera access, a QR/barcode library, and generating a unique code per delivery — meaningful build time for something that doesn't change the core architecture being tested (request → assignment → status flow). We prioritized proving that flow works end-to-end over adding a verification mechanism on top of it."]

**What we'd do with more time:** [e.g. "Generate a unique QR code per delivery at creation time; the rider scans it at drop-off, and the status only flips to Delivered if the scanned code matches — this would also solve 'right rider, right location' verification as a side benefit."]

---

### Trade-off 6 — SQLite on ephemeral storage (no data persistence across deploys/restarts)
**Owner:** Member 5

**What it is:** The app stores all data in a single SQLite file (`reflex.db`) written to local disk inside the running container. On our chosen host (Render, free tier), that disk is wiped every time the service redeploys, or spins down from inactivity and restarts. We confirmed this directly: after a fresh deploy, hitting `/riders` immediately returned the 3 seeded riders (Brian, Kevin, James) with no manual setup — proof the database is being recreated from scratch each time, not persisted from a prior run. Any deliveries created between deploys are lost.

**Acceptable because:** SQLite required zero extra infrastructure to stand up — no separate database service, no connection strings, no migrations — so the team could spend the sprint on the actual delivery-tracking logic the brief is graded on, not on provisioning a database. For proving the request → assignment → status flow works end-to-end in a live demo, losing data on redeploy has no visible cost — we control when redeploys happen, and the demo script re-seeds the same 3 riders every time regardless.

**What we'd do with more time:** Migrate to a managed Postgres instance (available natively on the same host) and swap the `sqlite3` calls in `models.py` for a proper DB driver/ORM. This also matters beyond just persistence: SQLite's file-level locking means it can't safely handle multiple concurrent writers, so it would block us from ever running more than one instance of the app — Postgres removes that ceiling too.

---

## Cross-check before submitting
- [ ] At least 3 trade-offs listed (brief's minimum)
- [ ] Each has all three parts filled in — what it is / why accepted / what we'd change
- [ ] These exact points match what Slide 6 of the deck says
- [ ] Each owner has rehearsed explaining their trade-off out loud, not just written it down
