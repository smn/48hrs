var Chat = (function() {

    var error_sleep_time = 500;

    var Chat = function() {};
    Chat.fn = Chat.prototype;


    Chat.fn.draw_messages = function(msgs) {
        console.log(msgs)
    };


    Chat.fn.past_messages = function(url, callback) {

        var that = this;
        $.ajax({
            url: url,
            success: function(r) {
                that.draw_messages(r);
                callback();
            },
            error: function() {

            }
        })
    };

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
                console.log('Poll error, sleeping for', error_sleep_time, 'ms');
                window.setTimeout(function() { that.live_messages(url) }, error_sleep_time);
            }
        });
    };

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
                console.log('could not post message');
            }

        });
    }


    return Chat;

})();
