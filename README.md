```python
$ python
Python 2.7.8 (default, Apr 30 2015, 22:44:47)
[GCC 4.2.1 Compatible Apple LLVM 6.1.0 (clang-602.0.49)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from vul_scraper import get_team_attendance
>>> from pprint import pprint
>>>
>>> auth = ('some_email@gmail.com', 'some_password')
>>>
>>> player_attendance = get_team_attendance(team_id=1906, league_id=159, auth=auth)
>>> pprint(player_attendance)
{'games': {1: {'female': {'coming': 5,
                          'maybe': 0,
                          'no response': 1,
                          'not coming': 0},
               'male': {'coming': 3,
                        'maybe': 1,
                        'no response': 2,
                        'not coming': 2}},
           2: {'female': {'coming': 5,
                          'maybe': 0,
                          'no response': 1,
                          'not coming': 0},
               'male': {'coming': 4,
                        'maybe': 0,
                        'no response': 2,
                        'not coming': 2}}}}
>>>
```
