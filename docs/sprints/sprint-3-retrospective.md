# 🧠 Sprint 3 Retrospective

## What Went Well (Minimum 3 Items)
1.  **High Velocity & Scope Completion:** We met 100% of the committed story points (19 points) and achieved the primary MVP goal ahead of schedule.
2.  **Successful Complex Integration:** Successfully implemented server-side token passing (JWT) to satisfy Supabase Row-Level Security (RLS) requirements, which was a major technical dependency.
3.  **Effective Debugging:** We were able to rapidly diagnose and resolve critical production issues (Foreign Key violation and RLS policy failures) by effectively linking live server logs (Render) to the database configuration (Supabase).

## What Didn't Go Well (Minimum 2 Items)
1.  **Deployment Friction:** We failed to correctly anticipate the necessary configuration for Render (setting environment variables) and database integrity (missing user profile data), which required significant debugging time post-deployment.
2.  **Overly Restrictive RLS Setup:** The initial RLS policies for `events` and `rsvps` were too simple, leading to multiple back-and-forth fixes on `WITH CHECK` conditions.

## What to Improve (Minimum 2 Items with Action Items)
1.  **Action Item: Standardize Deployment Checklist.** (Owner: [Classmate who handles Render], Deadline: Start of Sprint 4) — Before any future deployment, we will have a mandatory checklist to verify all secrets are set on Render and all necessary database initialization steps (like running the profile trigger) are documented for future environments.
2.  **Action Item: Proactive Database Testing.** (Owner: Nicolassirias, Deadline: Start of Sprint 4) — For any future CRUD features, we will manually test RLS policies in the Supabase SQL editor *before* writing the final integration code in Django.

---

## Team Dynamics Reflection
The team worked effectively together, especially when troubleshooting the complex authentication issues. The clear division of labor (coding vs. documentation/deployment) helped maintain focus. Communication was strong, leading to rapid resolution of blockers.
