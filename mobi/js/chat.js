var Chat = (function() {

    var error_sleep_time = 500;

    var Chat = function() {};
    Chat.fn = Chat.prototype;

    // generic method, should be overrriden to provide native drawing of messages.
    Chat.fn.draw_messages = function(msgs) {
        console.log(msgs)
    };

    // used only once to fetch messages in the past.
    Chat.fn.past_messages = function(url, callback) {

        var that = this;
        $.ajax({
            url: url,
            success: function(r) {
                that.draw_messages(r);
                callback();
            },
            error: function() {
                console.log("Error: Couldn't fetch past messages.")
            }
        })
    };


    // once called is always called to fetch live messages.
    // should open a long poll connection, and wait for a response,
    // when repsonse is received a new connection is immediatly opened.
    Chat.fn.live_messages = function(url) {
        var that = this;
        $.ajax({
            url: url,
            success: function(r) {
                that.draw_messages(r);
                error_sleep_time = 500;
                window.setTimeout(function() {that.live_messages(url)}, 1000); // change this to zero when testing live.
            },

            error: function(r) {
                error_sleep_time *= 2;
                window.setTimeout(function() { that.live_messages(url) }, error_sleep_time);
                console.log("Error: Coudln't fetch live messages, sleeping for", error_sleep_time, "ms");
            }
        });
    };

    // a simple xhr post.
    Chat.fn.post_message = function(url, msg, callback) {

        $.ajax({
            url: url,
            method: 'post',
            data: msg,
            success: function() {
                console.log('message was posted...');
                callback();
            },
            error: function() {
                console.log("Error: Couldn't post message");
            }

        });
    }


    return Chat;

})();
