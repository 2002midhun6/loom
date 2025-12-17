def save_user_details(backend, user, response, *args, **kwargs):
    """
    Custom pipeline step to save email and first_name from Google response.
    """
    if backend.name == 'google':
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')

       
        if email and not user.email:
            user.email = email
       
        if first_name and not user.first_name:
            user.first_name = first_name
       
        if last_name and not user.last_name:
            user.last_name = last_name
        
        user.save()