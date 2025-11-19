import logging
logger = logging.getLogger(__name__)

import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from supabase import create_client, Client
from django.utils import timezone

from .forms import EventForm

def _sb() -> Client | None:
    client = getattr(settings, "SUPABASE_CLIENT", None)
    if client:
        return client

    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    return create_client(url, anon_key)

def home(request):
    from django.utils.dateparse import parse_datetime
    
    events_list = []
    sb = _sb()
    sb_user_id = request.session.get("sb_user_id")
    access_token = request.session.get("sb_access_token")
    anon_key = getattr(settings, "SUPABASE_ANON_KEY", None)
    auth_was_set = False
    
    if sb:
        try:
            # Authenticate Supabase client with the user's token so RLS allows all events
            if access_token:
                sb.postgrest.auth(token=access_token)
                auth_was_set = True
            
            # Fetch all events from Supabase
            response = sb.table("events").select("*").order("datetime", desc=False).execute()
            
            # Fetch all RSVPs with user information (JOIN rsvps with users via foreign key)
            # Supabase PostgREST uses foreign key relationships for joins
            rsvps_response = sb.table("rsvps").select("event_id, user_id, users(name, email)").execute()
            
            # Also fetch all users to build a user_id -> name mapping
            users_response = sb.table("users").select("id, name, email").execute()
            users_map = {user.get("id"): user for user in users_response.data}
            
            # Get current user's info for display
            current_user_data = users_map.get(sb_user_id, {}) if sb_user_id else {}
            current_user_name = current_user_data.get("name") or current_user_data.get("email", "You") if current_user_data else None
            
            # Build a map of event_id -> list of attendees
            attendees_map = {}
            user_rsvps_map = {}  # Map of event_id -> True if current user has RSVP'd
            
            for rsvp in rsvps_response.data:
                event_id = rsvp.get("event_id")
                user_id = rsvp.get("user_id")
                
                if event_id:
                    if event_id not in attendees_map:
                        attendees_map[event_id] = []
                    
                    # Get user info from the joined data or fallback to users_map
                    user_data = rsvp.get("users")
                    # Handle case where users might be a list (if foreign key returns array)
                    if isinstance(user_data, list) and len(user_data) > 0:
                        user_data = user_data[0]
                    # If no joined data, use the users_map fallback
                    if not user_data or not isinstance(user_data, dict):
                        user_data = users_map.get(user_id, {})
                    
                    # Add user name or email as fallback
                    attendee_name = user_data.get("name") or user_data.get("email", "Unknown")
                    attendees_map[event_id].append(attendee_name)
                    
                    # Check if current user has RSVP'd
                    if sb_user_id and user_id == sb_user_id:
                        user_rsvps_map[event_id] = True
                        # Ensure current user's name is in the attendees list (in case of timing issues)
                        if current_user_name and current_user_name not in attendees_map[event_id]:
                            attendees_map[event_id].append(current_user_name)
            
            # Format events for template
            for event in response.data:
                event_id = event.get("id")
                
                # Parse datetime string to datetime object for template filters
                event_datetime = None
                if event.get("datetime"):
                    datetime_str = event.get("datetime")
                    # Try parsing as ISO format (Supabase typically returns ISO 8601)
                    event_datetime = parse_datetime(datetime_str)
                    # If that fails, try parsing as timestamp format
                    if not event_datetime:
                        from datetime import datetime
                        try:
                            event_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                        except (ValueError, TypeError):
                            pass
                    # Make timezone-aware if naive
                    if event_datetime and timezone.is_naive(event_datetime):
                        event_datetime = timezone.make_aware(event_datetime, timezone.get_current_timezone())
                
                # Get attendees for this event
                event_attendees = attendees_map.get(event_id, []).copy()
                
                # Ensure current user's name is in the list if they've RSVP'd
                has_rsvped = user_rsvps_map.get(event_id, False)
                if has_rsvped and current_user_name:
                    # Add current user's name if not already in the list
                    if current_user_name not in event_attendees:
                        event_attendees.append(current_user_name)
                
                events_list.append({
                    'id': event_id,  # Event ID for RSVP functionality
                    'title': event.get("title", ""),
                    'location_text': event.get("location_text", ""),
                    'datetime': event_datetime,
                    'description': event.get("description", ""),
                    'category': event.get("category"),  # Optional field
                    'has_rsvped': has_rsvped,  # Whether current user has RSVP'd
                    'attendees': event_attendees,  # List of attendee names (includes current user if RSVP'd)
                })
        except Exception as exc:
            logger.exception("Failed to fetch events from Supabase: %s", exc)
            # Continue with empty list on error
        finally:
            # Reset the client's token back to the anonymous key after the request
            if auth_was_set and anon_key:
                sb.postgrest.auth(token=anon_key)
    
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
                    url = os.getenv("SUPABASE_URL")
                    key = os.getenv("SUPABASE_ANON_KEY")
                    if not url or not key:
                        error = f"Server is missing Supabase credentials. URL: {'set' if url else 'missing'}, Key: {'set' if key else 'missing'}"
                    else:
                        error = "Supabase client failed to initialize. Check server logs."
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
                # Log full stack to server logs; show more helpful message to user
                logger.exception("Auth error (%s): %s", action, e)
                error_msg = str(e)
                # Extract more helpful error messages from Supabase exceptions
                if "Invalid API key" in error_msg or "JWT" in error_msg:
                    error = "Invalid Supabase API key. Please check your SUPABASE_ANON_KEY in .env file."
                elif "email" in error_msg.lower() or "password" in error_msg.lower():
                    error = f"Authentication failed: {error_msg[:100]}"
                else:
                    if action == "signup":
                        error = f"Sign up failed: {error_msg[:150]}"
                    else:
                        error = f"Sign in failed: {error_msg[:150]}"

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
    
    sb_user_id = request.session.get("sb_user_id")
    if not sb_user_id:
        return redirect("signin")

    form = EventForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        sb = _sb()
        if not sb:
            form.add_error(None, "Server is missing Supabase credentials.")
        else:
            # Retrieve the authenticated user's JWT Access Token from session
            access_token = request.session.get("sb_access_token")
            
            if not access_token:
                form.add_error(None, "Authentication session expired. Please sign in again.")
            else:
                # Get the anon key to reset after the request
                anon_key = getattr(settings, "SUPABASE_ANON_KEY", None)
                
                # Set the authenticated user's access token on the client
                sb.postgrest.auth(token=access_token)
                
                try:
                    event_date = form.cleaned_data["event_date"]
                    if timezone.is_naive(event_date):
                        event_date = timezone.make_aware(event_date, timezone.get_current_timezone())

                    payload = {
                        "title": form.cleaned_data["title"],
                        "description": form.cleaned_data["description"],
                        "datetime": event_date.isoformat(),
                        "location_text": form.cleaned_data["location"],
                        "creator_id": sb_user_id,
                    }

                    sb.table("events").insert(payload).execute()
                    # Reset the client's token back to the anonymous key for future use
                    if anon_key:
                        sb.postgrest.auth(token=anon_key)
                    return redirect("home")
                except Exception as exc:
                    logger.exception("Supabase insert failed: %s", exc)
                    # Reset the client's token back to the anonymous key even on error
                    if anon_key:
                        sb.postgrest.auth(token=anon_key)
                    form.add_error(None, "We could not save your event. Please try again.")

    return render(request, "core/event_form.html", {"form": form})

@require_POST
def rsvp_toggle(request, event_id):
    """Toggle RSVP for an event (INSERT if not RSVP'd, DELETE if already RSVP'd). Requires authentication."""
    if not request.session.get("sb_user_email"):
        return redirect("signin")
    
    sb_user_id = request.session.get("sb_user_id")
    if not sb_user_id:
        return redirect("signin")
    
    sb = _sb()
    if not sb:
        from django.contrib import messages
        messages.error(request, "Server is missing Supabase credentials.")
        return redirect("home")
    
    # Retrieve the authenticated user's JWT Access Token from session
    # MUST use 'sb_access_token' key (matches signin function storage)
    access_token = request.session.get("sb_access_token")
    
    if not access_token:
        from django.contrib import messages
        messages.error(request, "Authentication session expired. Please sign in again.")
        return redirect("signin")
    
    # Get the anon key to reset after the request
    anon_key = getattr(settings, "SUPABASE_ANON_KEY", None)
    
    # Set the authenticated user's access token on the client
    sb.postgrest.auth(token=access_token)
    
    try:
        # Check if user has already RSVP'd
        existing_rsvp = sb.table("rsvps").select("id").eq("event_id", event_id).eq("user_id", sb_user_id).execute()
        
        from django.contrib import messages
        
        if existing_rsvp.data and len(existing_rsvp.data) > 0:
            # User has RSVP'd - DELETE the RSVP
            sb.table("rsvps").delete().eq("event_id", event_id).eq("user_id", sb_user_id).execute()
            messages.success(request, "You've cancelled your RSVP for this event.")
        else:
            # User has NOT RSVP'd - INSERT new RSVP
            # RSVP payload - must use 'user_id' to match RLS policy: auth.uid() = user_id
            payload = {
                "user_id": sb_user_id,  # Crucial: must be 'user_id' for RLS policy
                "event_id": event_id,
            }
            sb.table("rsvps").insert(payload).execute()
            messages.success(request, "You've successfully RSVP'd to this event!")
        
        # Reset the client's token back to the anonymous key for future use
        if anon_key:
            sb.postgrest.auth(token=anon_key)
        
        return redirect("home")
    except Exception as exc:
        logger.exception("RSVP toggle failed: %s", exc)
        # Reset the client's token back to the anonymous key even on error
        if anon_key:
            sb.postgrest.auth(token=anon_key)
        from django.contrib import messages
        messages.error(request, "We could not update your RSVP. Please try again.")
        return redirect("home")
