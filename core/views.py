import logging
logger = logging.getLogger(__name__)

import os
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from supabase import create_client, Client
from django.utils.dateparse import parse_datetime

def _sb() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    return create_client(url, anon_key)

def home(request):
    from .models import Event
    from django.utils import timezone
    
    # Get all upcoming events (or all events if none upcoming)
    events = Event.objects.filter(time__gte=timezone.now())
    if not events.exists():
        # If no upcoming events, show all events
        events = Event.objects.all()[:20]  # Limit to recent 20
    
    # Format events for template (matching the expected structure)
    events_list = []
    for e in events:
        events_list.append({
            'title': e.name,
            'location_text': e.location,
            'datetime': e.time,
            'description': e.details,
            'category': None,  # Optional field
        })
    
    return render(request, "core/home.html", {'events': events_list})

@require_http_methods(["GET", "POST"])
def signin(request):
    error, info = None, None
    if request.method == "POST":
        action = request.POST.get("action", "signin")
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if not email or not password:
            error = "Please enter both email and password."
        else:
            try:
                sb = _sb()
                if not sb:
                    error = "Server is missing Supabase credentials."
                else:
                    if action == "signup":
                        if password != password_confirm:
                            error = "Passwords do not match."
                        else:
                            res = sb.auth.sign_up({"email": email, "password": password})
                            if getattr(res, "session", None):
                                request.session["sb_access_token"] = res.session.access_token
                                request.session["sb_refresh_token"] = res.session.refresh_token
                                request.session["sb_user_id"] = res.user.id
                                request.session["sb_user_email"] = res.user.email
                                return redirect("home")
                            else:
                                info = "Account created. Check your email if confirmation is required."
                    else:
                        auth_res = sb.auth.sign_in_with_password({"email": email, "password": password})
                        if auth_res and auth_res.session and auth_res.user:
                            request.session["sb_access_token"] = auth_res.session.access_token
                            request.session["sb_refresh_token"] = auth_res.session.refresh_token
                            request.session["sb_user_id"] = auth_res.user.id
                            request.session["sb_user_email"] = auth_res.user.email
                            return redirect("home")
                        else:
                            error = "Invalid email or password."
            except Exception as e:
                # Log full stack to server logs; show short message to user
                logger.exception("Auth error (%s): %s", action, e)
                if action == "signup":
                    error = "Sign up failed on the server. Please try again."
                else:
                    error = "Sign in failed on the server. Please try again."

    return render(request, "core/signin.html", {"error": error, "info": info})

@require_POST
def logout(request):
    for k in ["sb_access_token", "sb_refresh_token", "sb_user_id", "sb_user_email"]:
        request.session.pop(k, None)
    return redirect("signin")

@require_http_methods(["GET", "POST"])
def host_event(request):
    if not request.session.get("sb_user_email"):
        return redirect("signin")
    
    if request.method == "POST":
        from .models import Event
        from django.utils.dateparse import parse_datetime
        
        name = request.POST.get("name", "").strip()
        location = request.POST.get("location", "").strip()
        time_str = request.POST.get("time", "").strip()
        details = request.POST.get("details", "").strip()
        
        error = None
        if not name:
            error = "Event name is required."
        elif not location:
            error = "Location is required."
        elif not time_str:
            error = "Event time is required."
        else:
            # Parse datetime from form input (format: YYYY-MM-DDTHH:MM)
            try:
                from django.utils import timezone
                from datetime import datetime
                if 'T' in time_str:
                    event_time = parse_datetime(time_str)
                    # Make timezone-aware if it's naive
                    if event_time and not timezone.is_aware(event_time):
                        event_time = timezone.make_aware(event_time)
                else:
                    # Try to parse date-only format
                    from django.utils.dateparse import parse_date
                    date_obj = parse_date(time_str)
                    if date_obj:
                        event_time = timezone.make_aware(
                            datetime.combine(date_obj, datetime.min.time())
                        )
                    else:
                        event_time = None
                
                if not event_time:
                    error = "Invalid date/time format."
                else:
                    event = Event.objects.create(
                        name=name,
                        location=location,
                        time=event_time,
                        details=details,
                        host_email=request.session["sb_user_email"]
                    )
                    return redirect("home")
            except Exception as e:
                logger.exception("Error creating event: %s", e)
                error = "Error creating event. Please try again."
        
        # Re-fetch events for template when showing error
        from .models import Event
        from django.utils import timezone
        events = Event.objects.filter(time__gte=timezone.now())
        if not events.exists():
            events = Event.objects.all()[:20]
        events_list = []
        for e in events:
            events_list.append({
                'title': e.name,
                'location_text': e.location,
                'datetime': e.time,
                'description': e.details,
                'category': None,
            })
        return render(request, "core/home.html", {'events': events_list, 'error': error})
    
    # GET request - redirect to home (form will be in modal)
    return redirect("home")
