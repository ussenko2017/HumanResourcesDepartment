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

from docxtpl import DocxTemplate

doc = DocxTemplate("test.docx")
context = { 'var_name' : "HELLO WORLD!!!!!!!!!!!" }
doc.render(context)
doc.save("generated.docx")



import docx

doc = docx.Document('generated.docx')

# добавляем таблицу 3x3
table = doc.add_table(rows = 3, cols = 3)
# применяем стиль для таблицы


# заполняем таблицу данными
for row in range(3):
    for col in range(3):
        # получаем ячейку таблицы
        cell = table.cell(row, col)
        # записываем в ячейку данные
        cell.text = str(row + 1) + str(col + 1)

doc.save('generated.docx')