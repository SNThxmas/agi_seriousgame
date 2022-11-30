/* Reload after 20 seconds. */

var autoReload = function() {
    setTimeout(function() {
        location.reload();
    }, 20000);
}

autoReload();