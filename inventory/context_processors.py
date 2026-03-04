from .models import Career

def career_context(request):
    if not request.user.is_authenticated:
        return {"user_careers": [], "active_career": None}

    careers = list(request.user.userprofile.careers.all()) if hasattr(request.user, "userprofile") else []
    active_id = request.session.get("active_career_id")

    active = None
    if active_id:
        active = next((c for c in careers if c.id == active_id), None)

    # fallback: primera carrera
    if not active and careers:
        active = careers[0]
        request.session["active_career_id"] = active.id

    return {"user_careers": careers, "active_career": active}