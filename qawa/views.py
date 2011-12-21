from django.core.urlresolvers import reverse
from qawa.utils import pin_required, json_response, login_required
from qawa.forms import AuthForm, RegisterForm, GroupsForm, MessagesForm
from qawa.redis_utils import UserStore, GroupStore, MessageStore
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
import redis
import json

redis = redis.Redis()
user_store = UserStore(redis)
group_store = GroupStore(redis)
message_store = MessageStore(redis)

def get_form_errors_as_string(form):
    return ''.join([''.join([error for error in field.errors]) for field in form])

def auth(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            #password = form.cleaned_data['password']
            if not user_store.get(username):
                user_store.register(username)
                request.session[settings.QAWA_SESSION_KEY] = False
                request.session['qawa_username'] = None
                
            request.session[settings.QAWA_SESSION_KEY] = True
            request.session['qawa_username'] = username
            return redirect('home')
        else:
            return json_response({'auth': False, 'reason': get_form_errors_as_string(form)})
    
    if request.session[settings.QAWA_SESSION_KEY]:
        return redirect('home')
    
    form = AuthForm()
    return render(request, 'login.html', {'form': form})

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

@login_required
def home(request):
    return render(request, 'index.html')

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

@pin_required
def messages(request):
    username = request.session['qawa_username']
    user = user_store.find(username)
    
    if request.method == 'POST':
        form = MessagesForm(request.POST)
        if form.is_valid():            
            group = form.cleaned_data['group']
            message = form.cleaned_data['message']
            message_store.add(username, group[1:], message)
            return json_response('Created.', status = 201)
        else:
            return json_response(get_form_errors_as_string(form), status = 400)
    
    group = request.GET.get('channel')
    
    if group:
        return json_response(message_store.get_messages(group[1:]))
    return json_response('Please select a channel.', status = 400)

@pin_required
def live(request):
    group = request.GET.get('channel')
    username = request.session['qawa_username']

    if group:
        messages = message_store.get_live_messages(username, group[1:])
        return json_response(messages)
    return json_response('Please select a channel.', status = 400)