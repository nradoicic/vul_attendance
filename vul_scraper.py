import re
from copy import deepcopy
from urlparse import urljoin

import lxml.html
import requests

BASE_URL = 'https://www.vul.ca/'
TEAM_URL = urljoin(BASE_URL, '/team/{team_id}/league/{league_id}/')

def get_player_info(team_id, league_id, auth):
    session = requests.Session()
    drupal_login(session, auth)
    team_url = TEAM_URL.format(**locals())
    schedule_page = get_schedule(session, team_url)
    attendance_link = get_attendance_link(schedule_page)
    attendance_page = get_attendance(session, team_url, attendance_link)
    player_info = parse_player_info(attendance_page)
    return player_info

def drupal_login(session, auth):
    username, password = auth
    login_url = urljoin(BASE_URL, 'user/login')
    login_page = session.get(login_url).text
    login = lxml.html.fromstring(login_page)
    form_id_value = login.cssselect('input[name=form_build_id]')[0].value
    form_id = form_id_value.split('-')[1]
    data = {
        'name': username,
        'pass': password,
        'form_build_id': form_id,
        'form_id': 'user_login',
        'op': 'Log in'
    }
    login_submit = requests.post(login_url, data=data)
    cookies = login_submit.headers['Set-Cookie']

    # I should probably use http.cookies here but I don't wanted the added
    # dependency and this is one line...
    cookie_dict = {k.strip():v for k,v in re.findall(r'(.*?)=(.*?);', cookies)}
    session.cookies = requests.utils.cookiejar_from_dict(cookie_dict)

def file_string(filename):
    file_obj = open(filename)
    return file_obj.read()

def get_schedule(session, team_url):
    url = urljoin(team_url, 'schedule')
    schedule_page = session.get(url).text
    #schedule_page = file_string('schedule_page.html')
    return schedule_page

def get_attendance_link(schedule_page):
    parsed = lxml.html.fromstring(schedule_page)
    selector = '.scheduled-game td.attendance-totals > a'

    # We always want just the upcoming game
    attendance_link = parsed.cssselect(selector)[0].attrib['href']
    return attendance_link

def get_attendance(session, team_url, attendance_link):
    url = urljoin(team_url, attendance_link)
    attendance_page = session.get(url).text
    #attendance_page = file_string('attendance.html')
    return attendance_page

def parse_player_info(attendance_page):
    parsed = lxml.html.fromstring(attendance_page)
    selector = 'table.team-schedule tr'

    # We always want just the upcoming game
    player_info = {}
    gender = 'female'
    rows = parsed.cssselect(selector)
    for row in rows[3:]:
        if 'subheader' in row.attrib['class']:
            gender = 'male'
            continue
        name = row.text_content()
        attending_elements = row.cssselect('span.attending-status > *')
        attending = get_attending_statuses(attending_elements)
        note = row.cssselect('div.editable-field')[0].text_content() or None

        player_info[name] = {
            'gender': gender,
            'attending': attending,
            'note': note,
        }
    return player_info

def get_attending_statuses(attending_elements):
    return tuple(map(is_attending_human, attending_elements))

def is_attending(element):
    classes = element.attrib['class']
    if 'fa-check' in classes:
        return True
    elif 'fa-times' in classes:
        return False
    elif 'attendance-unknown' in classes:
        return 'maybe'
    else:
        return None

def is_attending_human(element):
    classes = element.attrib['class']
    if 'fa-check' in classes:
        return 'coming'
    elif 'fa-times' in classes:
        return 'not coming'
    elif 'attendance-unknown' in classes:
        return 'maybe'
    else:
        return 'no response'

def get_team_attendance(team_id, league_id, auth):
    gender = {
        'coming': 0,
        'not coming': 0,
        'maybe': 0,
        'no response': 0,
    }
    game = {
        'male': deepcopy(gender),
        'female': deepcopy(gender)
    }
    attendance = {
        1: deepcopy(game),
        2: deepcopy(game),
    }
    player_info = get_player_info(team_id, league_id, auth)
    for name,info in player_info.items():
        for game_number,attending in enumerate(info['attending'], 1):
            attendance[game_number][info['gender']][attending] += 1
    return {'games': attendance}
