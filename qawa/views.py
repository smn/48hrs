from django.core.urlresolvers import reverse
from qawa.utils import authenticate, pin_required, json_response
from django.conf import settings

def is_auth(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if authenticate(username, password):
                request.session[settings.UMMELI_PIN_SESSION_KEY] = True
                return render(request, 'auth.json',
                          {'form': form, 'auth': True})
            else:
                request.session[settings.UMMELI_PIN_SESSION_KEY] = False
                return json_response({'auth': False, 'reason': 'Cannot authenticate user.'})
        else:
            return json_response({'auth': False, 'reason': 'Form invalid.'})
        
    if request.session.get(settings.QAWA_SESSION_KEY):
        auth = True
    else:
        auth = False
        
    return json_response({'auth': auth, 'reason': 'You need to login first.'}, status = 403)
    
@pin_required
def home(request):
    return json_response({'message': 'Hello world!'})