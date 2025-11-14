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
    # renders event list (ok if you still have the simple version)
    return render(request, "core/home.html")

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
