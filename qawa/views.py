from django.core.urlresolvers import reverse
from qawa.utils import pin_required, json_response
from qawa.forms import AuthForm, RegisterForm
from qawa.redis_utils import UserStore
from django.conf import settings

user_store = UserStore()

def auth(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if user_store.authenticate(username, password):
                request.session[settings.QAWA_SESSION_KEY] = True
                return json_response({'auth': True})
            else:
                request.session[settings.QAWA_SESSION_KEY] = False
                return json_response({'auth': False, 'reason': 'Cannot authenticate user.'})
        else:
            errors = ''.join([''.join([error for error in field.errors]) for field in form])
            return json_response({'auth': False, 'reason': errors})

    if request.session.get(settings.QAWA_SESSION_KEY):
        return json_response({'auth': True})
    return json_response({'auth': False, 'reason': 'You need to login first.'}, status = 403)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if not user_store.user_exists(username):
                #TODO: send message to user telling them to reply with pin
                print 'TODO: smn'
                return json_response({'auth': True})
            else:
                return json_response({'error': 'Username is already taken.'})

        return json_response({'error': 'Username is a required field.'})
    return json_response({'error': 'Not implemented.'}, status = 501)

@pin_required
def home(request):
    return json_response({'message': 'Hello world!'})