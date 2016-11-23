# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from datetime import datetime
from datetime import timedelta
from collections import namedtuple

app = Flask(__name__)
#app.run(host='0.0.0.0')

Segment = namedtuple("Segment", "index duration eventtype")

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/edit', methods = ['POST'])
def edit():
    day = request.form['day']
    hour = request.form['hour']
    filename = day + "_" + hour
    f = open('timeslots/' + filename, 'r')
    contents = f.read()
    f.close()
    segments = []
    tokens = contents.split("b")
    i = 1
    for t in tokens:
        if len(t) > 2:
            q = t.split("a")
            txt = ""
            if int(q[1]) == 1:
                txt += "Reklama"
            elif int(q[1]) == 2:
                txt += "Audycja"
            elif int(q[1]) == 3:
                txt += "Muzyka"
            elif int(q[1]) == 4:
                txt += "Dziennik"
            elif int(q[1]) == 5:
                txt += "Rozmowa"
            elif int(q[1]) == 6:
                txt += "Pogoda"
            segments.append(Segment(index=i, duration=int(q[0]), eventtype=txt))
            i += 1
    day_str = ""
    if day == "mon":
        day_str = u"Poniedziałek"
    elif day == "tue":
        day_str = u"Wtorek"
    elif day == "wed":
        day_str = u"Środa"
    elif day == "thu":
        day_str = u"Czwartek"
    elif day == "fri":
        day_str = u"Piątek"
    elif day == "sat":
        day_str = u"Sobota"
    elif day == "sun":
        day_str = u"Niedziela"
    hour_str = ""
    if len(hour) < 2:
        hour_str = "0" + hour + ":00"
    else:
        hour_str = hour + ":00"
    return render_template('edit.html', segments=segments, hour=hour_str, day=day_str, day_stc=day, hour_str=hour)

@app.route('/save', methods = ['POST'])
def save():
    day = request.form['day']
    hour = request.form['hour']
    plan = request.form['plan']
    filename = day + "_" + hour
    f = open('timeslots/' + filename, 'w')
    f.write(plan)
    f.close()
    return redirect(url_for('admin'))

@app.route('/')
def index():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second
    wday = now.weekday()
    wday_str = ""
    if minute < 10:
        minute_str = '0' + str(minute)
    else:
	minute_str = str(minute)
    current_time = str(hour) + ':' + minute_str
    if hour < 6 or hour > 19 or wday == 5 or wday == 6:
	return render_template('disabled.html')
    if wday == 0:
        wday_str = "mon"
    elif wday == 1:
        wday_str = "tue"
    elif wday == 2:
        wday_str = "wed"
    elif wday == 3:
        wday_str = "tue"
    elif wday == 4:
        wday_str = "fri"
    elif wday == 5:
        wday_str = "sat"
    elif wday == 6:
        wday_str = "sun"
    filename = wday_str + "_" + str(hour)
    f = open('timeslots/' + filename, 'r')
    contents = f.read()
    f.close()
    segments = []
    tokens = contents.split("b")
    i = 1
    for t in tokens:
        if len(t) > 2:
            q = t.split("a")
            txt = ""
            if int(q[1]) == 1:
                txt += "Reklama"
            elif int(q[1]) == 2:
                txt += "Audycja"
            elif int(q[1]) == 3:
                txt += "Muzyka"
            elif int(q[1]) == 4:
                txt += "Dziennik"
            elif int(q[1]) == 5:
                txt += "Studio"
            elif int(q[1]) == 6:
                txt += "Pogoda"
            segments.append(Segment(index=i, duration=int(q[0]), eventtype=txt))
            i += 1
    data_code = "["
    colors_dict = {
        "Reklama" : "#4da74d",
        "Audycja" : "#afd8f8",
        "Muzyka" : "#cb4b4b",
        "Dziennik" : "#edc240",
        "Pogoda" : "#8cacc6",
        "Studio" : "#9440ed"
    }
    sum = 0
    data_code += u"{label: \"Wykorzystany czas\", data: " + str(minute) + ", color: \"#dddddd\"},"
    for s in segments:
        sum += s.duration
        if sum > minute:
            if sum - minute < s.duration:
                data_code += u"{label: \"" + s.eventtype + "\", data: " + str(sum - minute) + ", color: \"" + colors_dict[s.eventtype] + "\"},"
            else:
                data_code += u"{label: \"" + s.eventtype + "\", data: " + str(s.duration) + ", color: \"" + colors_dict[s.eventtype] + "\"},"
    data_code += "]"
    current_block = ""
    next_block = ""
    sum = 0
    current_block_time_perc = 0
    for s in segments:
        sum += s.duration
        if sum > minute:
            current_block = s.eventtype
            current_block_start_time = sum - s.duration
            current_block_time_perc = ((minute + second/60.)-current_block_start_time)/s.duration*100
            s1 = now.strftime('%H:%M:%S')
            s2 = str(hour) + ':' + str(sum) + ':00'
            if sum == 60:
                s2 = str(hour+1) + ':00:00'
		if hour+1 == 24:
			s2 = '00:00:00'

            FMT = '%H:%M:%S'
            tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

            current_block_time_text = "-" + str(tdelta.seconds/60) + " min. " + str(tdelta.seconds-(tdelta.seconds/60)*60) + " sek."
            try:
                next_block = segments[segments.index(s)+1].eventtype
            except:
                next_block = "Kolejna playlista"
            break
    return render_template('index.html',
                           data_code=data_code,
                           current_block=current_block,
                           next_block=next_block,
                           current_block_time_perc=current_block_time_perc,
                           current_block_time_text=current_block_time_text,
			   current_time=current_time)
