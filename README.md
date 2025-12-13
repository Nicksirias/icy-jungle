# Social Butterfly

## Project Overview

Social Butterfly is a full-stack web application designed to help users create, discover, and attend local social events without relying on closed social networks or private invitation systems. The application targets students and young professionals who are new to an area and want to find open, community-driven events.

Users can sign up, browse upcoming events, filter by category, RSVP to events, and manage their attendance. Event hosts can create and manage events while viewing attendee lists. The application emphasizes simplicity, accessibility, and community engagement.

The project was developed using Agile/Scrum practices across four sprints and deployed to both staging and production environments.

---

## Technology Stack

- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Django Templates
- **Authentication:** Django built-in authentication system
- **Hosting:** Render
- **Version Control:** Git & GitHub

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL (optional for local use; SQLite can be used for development)
- Git

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/Nicksirias/icy-jungle.git
cd icy-jungle

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver

---
This application will be available at:
http://127.0.0.1:8000/

---
Deployment
Environments

Staging: Used during development and QA

Production: Final submission environment

Production URL
https://icy-jungle.onrender.com

Deployment Process

Development occurs on feature branches

Changes are merged via Pull Requests

Merging into main triggers automatic deployment on Render

All configuration and secrets are managed via environment variables

Core Features (MVP)

User registration and login

Event creation and management (create, edit, delete)

Event browsing and category filtering

RSVP system with attendee tracking

User dashboard for managing RSVPs

Responsive and clean UI

A/B Test Endpoint (Required)
Team Nickname
icy-jungle

How the Endpoint Is Computed

The A/B test endpoint is computed as the first 7 characters of the SHA-1 hash of the team nickname:
echo -n "icy-jungle" | shasum | cut -c1-7

A/B Test Endpoint URL
https://icy-jungle.onrender.com/da1801a/

Endpoint Behavior

Publicly accessible (no login required)

Displays all team member nicknames

Includes a button with id="abtest"

Button text alternates between:

Variant A: "kudos"

Variant B: "thanks"

Variant is randomly assigned and persisted per visitor session

Server-side analytics track page views and button clicks

Team Members

fair-hare
crowded-cat
adventurous-goldfish
crowded-crow
kind-bee

## Agile Development Summary

The project was developed using Scrum across four sprints:

Sprint 1: Design Sprint (user research, planning, wireframes)

Sprint 2: Infrastructure & initial deployment

Sprint 3: Core user journey implementation

Sprint 4: MVP polish, UI refinement, and A/B testing

All sprint documentation (planning, review, retrospective) is included in:
/docs/sprints/

Testing & Code Quality

Automated unit and integration tests for critical user flows

Database migrations tracked in version control

Django-appropriate linting applied

No secrets committed to the repository

Clear separation of concerns following MVC principles

Repository Links

GitHub Repository: https://github.com/Nicksirias/icy-jungle

Production App: https://icy-jungle.onrender.com

A/B Test Endpoint: https://icy-jungle.onrender.com/da1801a/

Sprint Documentation: /docs/sprints/

License

This project was developed for academic purposes as part of a course assignment.
