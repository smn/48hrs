from django.core.urlresolvers import reverse
from qawa.utils import pin_required, json_response
from qawa.forms import AuthForm, RegisterForm, GroupsForm
from qawa.redis_utils import UserStore, GroupStore
from django.conf import settings
import redis

redis = redis.Redis()
user_store = UserStore(redis)
group_store = GroupStore(redis)

def get_form_errors_as_string(form):
    return ''.join([''.join([error for error in field.errors]) for field in form])

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
            return json_response({'auth': False, 'reason': get_form_errors_as_string(form)})

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
                return json_response({'auth': False, 'reason': 'Username is already taken.'})    
            
        return json_response({'auth': False, 'reason': 'Username is a required field.'})
    return json_response({'auth': False, 'reason': 'Not implemented.'}, status = 501)

@pin_required
def home(request):
    return json_response({'message': 'Hello world!'})

@pin_required
def groups(request):
    if request.method == 'POST':
        form = GroupsForm(request.POST)
        if form.is_valid():            
            name = form.cleaned_data['name']
            if not group_store.exists(name):
                group_store.create(name, {'name': name})
                return json_response('Created.', status = 201)
            else:
                return json_response('Group already exists.', status = 400)
        else:
            return json_response(get_form_errors_as_string(form), status = 400)
    return json_response(group_store.all())