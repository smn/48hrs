48hrs app
=========

Idea for an app to be hacked together in 48 hrs or less using http://github.com/praekelt/vumi & http://github.com/praekelt/jmbo

SMS part
--------

Allow for simple group texting via SMS. Replicate mailing list type behaviour over SMS messages.

* [...] indicates optional argument
* <...> indicates mandatory argument
* `+` and `-` reserved for adding & deleting members
* `#` reserved for groups
* `?` reserved for querying
* `+27761234567 [name]` to add to the default group. Default group is the group without a #hashtag
* `-27761234567` to remove from the default group
* Any text sent to the number without this is automatically broadcast to the group. No #hashtag defaults to the default group. The first #hashtag occurrence is considered to be the name of the group targetted. So `Hi #coffeelovers, meeting at 9 in Kalkbay` would go to #coffeelovers.
* Any replies received are automatically broadcast to all recipients in the group. Replies will be prefixed with either the name or the number before being broadcast. Replies to groups other than the default group will need to be prefixed with the group #hashtag.
* New members will be automatically sent an invitation SMS to join the group, either via SMS or Mobi.

Group behaviour
~~~~~~~~~~~~~~~

Optional groups created via #hashtags

* `#<groupname> +27761234567 [name]` adds the number to the given group, if the group doesn't exist yet it will be created.
* `#<groupname> -27761234567` removes the number from the group, if the group is empty it will automatically be deleted.
* `?groups` returns a list of all groups available.

Mobi part
---------

Each group will have its own unique URL for group messaging, this URL should be included in the invitation SMS message.
The UI should be similar to a regular IM chat application:

* top part with incoming messages (scrolled down & newest automatically appended at the bottom)
* bottom part a text input field for message submission
* Needs to allow for a listing of groups
* Needs to allow for the creation & deletion of groups

The experience to be as realtime as possible and have two options:

**Sexy WebSockets** but the implementation of that cross browser is going to be tricky.

**Boring HTTP long polling**, which is easier to implement and Twisted and handle very well. This would require opening an HTTP connection which Twisted keeps open until a new message arrives, as soon as it arrives Twisted publishes the results and closes the HTTP connection. When the client Javascript processes the JSON payload with (1...n messages in it) it'll reconnect and wait for more messages.

The UI can be as plain and boring as necesary, we can add more visual sexy when we have functionality to design for.