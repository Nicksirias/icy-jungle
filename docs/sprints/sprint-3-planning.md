# 📅 Sprint 3 Planning Document

## Sprint Goal
**Goal:** Complete the core Event Management user journey: Users can sign up, create an event, view all events, and successfully RSVP/cancel an RSVP to an event.

---

## Selected User Stories from Backlog

We committed to completing the following core stories to achieve the MVP goal:

| User Story | Story Points | Team Assignment |
| :--- | :--- | :--- |
| **US-005:** As a user, I want to create an event so others can see and join it. | 5 | Nicolassirias |
| **US-006:** As a user, I want to see a list of all upcoming events on the homepage so I can browse options. | 3 | Nicolassirias |
| **US-007:** As a logged-in user, I want to RSVP to an event so my spot is confirmed. | 5 | Nicolassirias |
| **US-008:** As a logged-in user, I want to cancel my RSVP so my spot is freed up. | 3 | Nicolassirias |
| **US-009:** As a user, I want to see a list of attendees for an event so I know who is going. | 3 | Team Member 2 |

**Story Points Committed:** 19 points

---

## Dependencies and Risks

* **Dependency:** Successful integration of the Supabase Python client for server-side authenticated requests (CRUD operations).
* **Risk:** Row-Level Security (RLS) policies blocking authenticated database interactions.
* **Mitigation:** Prioritize setting up a dedicated Supabase client function within the Django project to handle JWT token passing for RLS compliance.
