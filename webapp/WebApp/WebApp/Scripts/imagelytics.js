var imagelytics = {

    unexpectedError: function (jqXHR) {
        bootbox.alert({
            title: "<i class='fa fa-exclamation-triangle'></i> Unexpected error",
            message: "Please refresh the page and try again.<br/>If the problem persists, please contact us.<br/><br/>Error Code: " + jqXHR.status + " (" + jqXHR.statusText + ")",
            buttons: {
                ok: {
                    label: '<i class="fa fa-times"></i> Close',
                    className: 'btn btn-primary no-bottom-margin'
                }
            }
        });
    },

    error: function (msg) {
        bootbox.alert({
            title: "<i class='fa fa-exclamation-triangle '></i> Error",
            message: msg,
            buttons: {
                ok: {
                    label: '<i class="fa fa-times"></i> Close',
                    className: 'btn btn-primary no-bottom-margin'
                }
            }
        });
    },

    info: function (msg) {
        bootbox.alert({
            title: "<i class='fa fa-info-circle '></i> Info",
            message: msg,
            buttons: {
                ok: {
                    label: '<i class="fa fa-times"></i> Close',
                    className: 'btn btn-primary no-bottom-margin'
                }
            }
        });
    },

    confirmButtons: {           
        cancel: {
            label: '<i class="fa fa-times"></i> Cancel',
            className: 'btn btn-default no-bottom-margin'
        },
        confirm: {
            label: '<i class="fa fa-check"></i> OK',
            className: 'btn btn-primary no-bottom-margin'
        }        
    },

    postJSON: function (url, data, callback) {
        $.post(url, data, function (response) {
            if (callback != null) {
                callback(response);
            }
        }, 'json').fail(function (jqXHR) { imagelytics.unexpectedError(jqXHR) });
    },
    
    nameWithoutExtension: function (filename) {        
        var dot = filename.lastIndexOf(".")
        if (dot > 0) {
            return filename.substring(0, dot);
        } else {
            return filename;
        }
    }
}