/* Return to the previous page after 5s */

var autoReturn = function() {
    setTimeout(function() {
        window.history.back();
    }, 3000);
}

autoReturn();