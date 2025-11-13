import logging
logger = logging.getLogger(__name__)

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from supabase import create_client, Client
from django.utils.dateparse import parse_datetime
from .models import Event, RSVP

def _sb() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    return create_client(url, anon_key)

def home(request):
    # Fetch all events ordered by datetime
    events = Event.objects.all()
    
    # For each event, check if current user has RSVP'd
    user_id = request.session.get("sb_user_id")
    for event in events:
        event.has_rsvpd = False
        if user_id:
            event.has_rsvpd = RSVP.objects.filter(event=event, user_id=user_id).exists()
        event.rsvp_count = event.rsvps.count()
    
    return render(request, "core/home.html", {"events": events})

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
def create_event(request):
    """Handle event creation - GET returns JSON for modal, POST creates event."""
    if not request.session.get("sb_user_id"):
        if request.method == "POST":
            return JsonResponse({"error": "You must be signed in to create events."}, status=403)
        return redirect("signin")
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        location = request.POST.get("location", "").strip()
        datetime_str = request.POST.get("datetime", "").strip()
        details = request.POST.get("details", "").strip()
        
        if not name or not location or not datetime_str:
            return JsonResponse({"error": "Name, location, and date/time are required."}, status=400)
        
        try:
            event_datetime = parse_datetime(datetime_str)
            if not event_datetime:
                return JsonResponse({"error": "Invalid date/time format."}, status=400)
        except Exception as e:
            logger.exception("Error parsing datetime: %s", e)
            return JsonResponse({"error": "Invalid date/time format."}, status=400)
        
        try:
            event = Event.objects.create(
                name=name,
                location=location,
                datetime=event_datetime,
                details=details,
                host_user_id=request.session["sb_user_id"],
                host_email=request.session["sb_user_email"]
            )
            return JsonResponse({
                "success": True,
                "message": "Event created successfully!",
                "event_id": event.id
            })
        except Exception as e:
            logger.exception("Error creating event: %s", e)
            return JsonResponse({"error": "Failed to create event. Please try again."}, status=500)
    
    # GET request - shouldn't normally happen, but return success
    return JsonResponse({"error": "Use POST to create events."}, status=405)

def event_detail(request, event_id):
    """Get event details as JSON for modal display."""
    event = get_object_or_404(Event, id=event_id)
    user_id = request.session.get("sb_user_id")
    
    has_rsvpd = False
    if user_id:
        has_rsvpd = RSVP.objects.filter(event=event, user_id=user_id).exists()
    
    rsvps = RSVP.objects.filter(event=event).select_related()
    rsvp_list = [{"user_email": r.user_email, "created_at": r.created_at.isoformat()} for r in rsvps]
    
    return JsonResponse({
        "id": event.id,
        "name": event.name,
        "location": event.location,
        "datetime": event.datetime.isoformat(),
        "details": event.details,
        "host_email": event.host_email,
        "created_at": event.created_at.isoformat(),
        "has_rsvpd": has_rsvpd,
        "rsvp_count": len(rsvp_list),
        "rsvps": rsvp_list
    })

@require_POST
def rsvp(request, event_id):
    """Handle RSVP submission."""
    if not request.session.get("sb_user_id"):
        return JsonResponse({"error": "You must be signed in to RSVP."}, status=403)
    
    event = get_object_or_404(Event, id=event_id)
    user_id = request.session["sb_user_id"]
    user_email = request.session["sb_user_email"]
    
    # Check if already RSVP'd
    if RSVP.objects.filter(event=event, user_id=user_id).exists():
        return JsonResponse({"error": "You have already RSVP'd to this event."}, status=400)
    
    try:
        rsvp_obj = RSVP.objects.create(
            event=event,
            user_id=user_id,
            user_email=user_email
        )
        return JsonResponse({
            "success": True,
            "message": "RSVP successful!",
            "rsvp_count": event.rsvps.count()
        })
    except Exception as e:
        logger.exception("Error creating RSVP: %s", e)
        return JsonResponse({"error": "Failed to RSVP. Please try again."}, status=500)
