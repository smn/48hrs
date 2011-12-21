from functools import wraps
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
import json

def pin_required(function):
    """
    Decorator to ask people to verify their pin before being able to access a view.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.session.get(settings.QAWA_SESSION_KEY):
            return function(request, *args, **kwargs)
            
        return json_response({'auth': False, 'reason': 'You need to login first.'}, status = 403)
                    
    return wrapper

def login_required(function):
    """
    Decorator to ask people to verify their pin before being able to access a view.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.session.get(settings.QAWA_SESSION_KEY):
            return function(request, *args, **kwargs)
            
        return redirect('auth')
                    
    return wrapper

def json_response(data, status = 200):
    return HttpResponse(json.dumps(data), status = status, content_type='application/json')