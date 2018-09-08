#!/bin/python3

import re

def random_switch_in_url(url):
    """Randomized replacement from a switch statement in curly braces within a URL"""
    regex = r"\{(.*?)\}"
    switched_url = ''
    matches = re.finditer(regex, urlf)
    for matchNum, match in enumerate(matches):
        print('{}, {}, {}'.format(matchNum, match.span(), match.groups()[0]))

    return switched_url

urlf = 'https://{switch:a,b,c,d}.tiles.mapbox.com/v4/digitalglobe.0a8e44ba/{zoom}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZGFrZ3pjczNpaHYycXFyMGo0djY3N2IifQ.90uebT4-ow1uqZKTUrf6RQ'

new_url = random_switch_in_url(urlf)
print(new_url)
