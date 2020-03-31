def show_alert(alert_type,header, body):
    """
    def x():
        alert_html = request.args.get('alert_html')
        if alert_html is None:
            alert_html = ''

    return render_template('x.html',alert_html=alert_html)


     alert_html = Flask.mod.show_alert('success', 'Отлично! ', 'данные сохранены')
    return flask.redirect(flask.url_for('x', alert_html=alert_html))
    """
    #success
    #info
    #warning
    #danger
    html = '<div class="showback"><div class="alert alert-'+alert_type+'">' \
           '<b>'+header+'</b> ' \
           ''+body+'</div></div>'
    return html