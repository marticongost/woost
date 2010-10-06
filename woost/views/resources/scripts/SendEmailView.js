/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".SendEmailView", function ($sendEmailView) {
    setTimeout("update_progress(" + this.thread_id + ")", 3000);
});

function update_progress(thread_id, edit_stack) {

    var url = "./send_email/mailing_state/" + thread_id
    if (edit_stack)
        url += "?edit_stack=" + edit_stack

    jQuery.getJSON(url, function(data) {
        if (!data) {
            jQuery(".mailing_info").html(jQuery("<div>").addClass("error_box").text(cocktail.translate("woost.extensions.mailer.SendEmailView error email delivery")));
        } else {

            if (data.alive) {
                setTimeout("update_progress(" + thread_id + ", '" + data.edit_stack + "')", 3000);
            } else {
                jQuery(".mailing_info h3").text(cocktail.translate("woost.extensions.mailer.SendEmailView email delivery finished"));
                if (data.mailer_errors != 0) {
                    jQuery(".mailing_info").append(jQuery("<div>").addClass("error_box").text(cocktail.translate("woost.extensions.mailer.SendEmailView error email delivery")));
                }
            }

            jQuery(".mailing_info .progress").css("width", data.progress + "%");
            jQuery(".mailing_info .progress-text").text(data.progress + "%");
            jQuery(".mailing_info .summary").html(cocktail.translate("woost.extensions.mailer.SendEmailView mailer summary").format((parseInt(data.emails_sent) - parseInt(data.mailer_errors)), parseInt(data.num_receivers)));
        }
    });
}

String.prototype.format = function(){
    var pattern = /\{\d+\}/g;
    var args = arguments;
    return this.replace(pattern, function(capture){ return args[capture.match(/\d+/)]; });
}
