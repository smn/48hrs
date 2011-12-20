JSON API
========

Authentication mechanism
------------------------

I suspect cookie based authentication is going to be easier than HTTP Auth when being used with Ajax.

Authentication
--------------

All URL endpoints should return some sensible HTTP header that means 'sod off, you need to authenticate first'.

GET /auth.json if authenticated

::

    {
        auth: true
    }

GET /auth.json if not authenticated

::

    {
        auth: false,
        reason: 'human friendly reason',
    }

POST /auth.json with `username` and `password`

::

    {
        auth: true
    }
    
::

    {
        auth: false,
        reason: 'human friendly reason',
    }


Groups
------

GET /groups.json

::

    [{
        name: '#coffelovers'
    },{
        name: '#soccer'
    }]


POST /groups.json with `name` should return HTTP 201 created

DELETE /groups.json with `name` should return HTTP 204


Message retrieval
-----------------

GET /messages.json with `group` parameter

::

    [{
        'author': 'name or MSISDN of message poster',
        'timestamp': 'timestamp in UTC ISO format',
        'message': 'the message posted',
    },{
        ...
    },{
        ...
    }]

