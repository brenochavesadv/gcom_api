
def get_permissions(user):
    return [p.name for p in user.role.permissions] if user.role else []
