import datetime

from google.appengine.ext.webapp import template

register = template.create_template_register()

def formatDateDistance(d):
    if d is None:
        return "Some time ago"

    d2 = datetime.datetime.today()
    dist = d2 - d
    distInSeconds = dist.total_seconds()

    if distInSeconds < 60:
        when = "Now"
    elif 60 <= distInSeconds < 3600:
        when = "About %d minutes ago" % (int(distInSeconds / 60), )
    elif 3600 <= distInSeconds < 86400:
        when = "About %d hours ago" % (int(distInSeconds / 3600), )
    elif 86400 <= distInSeconds < 86400 * 30:
        when = "About %d days ago" % (int(distInSeconds / 86400), )
    else:
        yearsDiff = int(distInSeconds / (86400 * 365))
        monthsDiff = int((distInSeconds - yearsDiff * 86400 * 365) / (86400 * 30))
        if yearsDiff > 0:
            # Disabled until the JavaScript can parse this:
            # when = "About %d years %d months ago" % (yearsDiff, monthsDiff)
            when = "About %d years ago" % (yearsDiff, )
        else:
            when = "About %d months ago" % (monthsDiff, )
    return when

register.filter('formatDateDistance', formatDateDistance)
