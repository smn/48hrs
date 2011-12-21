from django.core.urlresolvers import reverse
from qawa.utils import pin_required, json_response
from qawa.forms import AuthForm, RegisterForm, GroupsForm, MessagesForm
from qawa.redis_utils import UserStore, GroupStore
from django.conf import settings
from django.shortcuts import render
import redis
import random

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

def home(request):
    return render(request, 'index.html')

#@pin_required
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

#@pin_required
def messages(request):
    if request.method == 'POST':
        form = MessagesForm(request.POST)
        if form.is_valid():            
            group = form.cleaned_data['group']
            message = form.cleaned_data['message']
            if group_store.exists(group):
                #message_store.add(group, message)
                return json_response('Created.', status = 201)
            else:
                return json_response('Group not found.', status = 400)
        else:
            return json_response(get_form_errors_as_string(form), status = 400)
    return json_response([])

#@pin_required
def live(request):
    channel = request.GET.get('channel')
    messages1 = [
    {
        "author": "Susan",
        "timestamp": "timestamp in UTC ISO format",
        "message": "Did you really name your son Robert'); Drop Table Students;--?"
    },
    {
        "author": "John",
        "timestamp": "timestamp in UTC ISO format",
        "message": "Oh yes. Little Bobby tables we call him."
    }]
    
    messages2 = [
    {
        "author": "Susan",
        "timestamp": "timestamp in UTC ISO format",
        "message": "Hi! I'm new here."
    }]
    
    messages3 = [
    {
        "author": "Paul",
        "timestamp": "timestamp in UTC ISO format",
        "message": "What lovely weather we having today!"
    }]
    
    rand_store = [[], messages1, messages2, messages3]
    if channel:
        #get live message for a particular group
        return json_response(rand_store[random.choice([0,0,0,1,0,2,0,0,3])])
    return json_response('Please select a channel.', status = 400)