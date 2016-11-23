/*
 Event function to make sure it is called after image load even if 'load' event is
 bind after the image has been loaded that is in case image is cached.
 It’s not the caching per se that is the problem but the timing: the images may
 already have been loaded by the time the event handler is attached (so it never gets fired).
 This may also occur if no caching happens, for example in a multithreaded browser on a
 very fast connection.
*/
jQuery.fn.extend({
    ensureLoad: function(handler) {
        return this.each(function() {
            if(this.complete) {
                handler.call(this);
            } else {
                $(this).load(handler);
            }
        });
    }
});

$(document).ready(function() {
    // Image events
    $(".image_loading").ensureLoad(function(){
        // Remove loading image from background
        $(this).css('background-image','none');
    });
});
