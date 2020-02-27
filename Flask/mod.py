def show_alert(alert_type,header, body):
    #success
    #info
    #warning
    #danger
    html = '<div class="showback"><div class="alert alert-'+alert_type+'">' \
           '<b>'+header+'</b> ' \
           ''+body+'</div></div>'
    return html