# 🏁 Sprint 3 Review Document

## Sprint Goal Achievement
**Goal:** Complete the core Event Management user journey.
**Achievement:** **ACHIEVED** ✅

We successfully implemented the complete, end-to-end user journey for the MVP.

---

## Completed User Stories

| User Story | Status | Story Points | Links (Example) |
| :--- | :--- | :--- | :--- |
| **US-005:** Create Event | COMPLETE | 5 | [Link to PR #10] |
| **US-006:** Browse Events | COMPLETE | 3 | [Link to PR #10] |
| **US-007:** RSVP to an Event | COMPLETE | 5 | [Link to PR #11] |
| **US-008:** Cancel RSVP | COMPLETE | 3 | [Link to PR #11] |
| **US-009:** See Attendee List | COMPLETE | 3 | [Link to PR #11] |

**Planned vs Completed Story Points:** 19 planned, **19 completed**.

---

## Demo Notes: Demonstrable User Journey
The complete user journey that can be demonstrated on the staging environment is:

1.  **User Sign Up/Login** (via Supabase Auth).
2.  **Create New Event:** User clicks 'Create Event', fills out the form, and submits. The event appears on the homepage.
3.  **RSVP and Display:** User clicks 'RSVP'. The button immediately toggles to **'CANCEL RSVP'**, and the user's name is added live to the **Attendees** list for that event.
4.  **Cancel RSVP:** User clicks 'CANCEL RSVP', and their name is instantly removed from the attendee list.

---

## Metrics

* **Planned Story Points:** 19
* **Completed Story Points (Sprint 3):** 19
* **Velocity for Sprint 3:** 19 points
* **Cumulative Velocity (Sprints 2-3):** [X (Sprint 2) + 19 (Sprint 3) = Z points]

## Backlog Refinements
* Prioritized styling and user feedback (Task: Improve card design).
* Added task to implement Edit/Delete functionality, restricted to the event creator.
