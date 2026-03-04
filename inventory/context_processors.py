def career_context(request):
    if not request.user.is_authenticated:
        return {"user_careers": [], "active_career": None}

    profile = getattr(request.user, "userprofile", None)
    careers = list(profile.careers.all()) if profile else []
    active_id = request.session.get("active_career_id")

    active = None
    if active_id:
        active = next((career for career in careers if career.id == active_id), None)

    if not active and careers:
        active = careers[0]
        request.session["active_career_id"] = active.id

    return {"user_careers": careers, "active_career": active}
