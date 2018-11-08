#!/usr/bin/python3
"""
"""
# Ivan Buendia Gayton, Humanitarian OpenStreetMap Team/Ramani Huria, 2018
import sys, os
import re
import random

def main(url):
    regex = r"\{switch:(.*?)\}"
    matches = re.finditer(regex, url, re.MULTILINE | re.DOTALL)
    switchedchoice = ''
    for match in matches:
        contents = match.group(1)
        switchedchoice = random.choice(contents.split(','))
    newurl = re.sub(regex, switchedchoice, url)        
        
    return newurl
    
if __name__ == "__main__":
    #main(sys.argv[1])
    print(main('http://t{switch:0,1,2,3}.tiles.virtualearth.net/tiles/a{quadkey}.jpeg?g=854&mkt=en-US&token=AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn'))
    print('\n')
    print(main('https://{switch:a,b,c,d}.tiles.mapbox.com/v4/digitalglobe.0a8e44ba/{zoom}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZGFrZ3pjczNpaHYycXFyMGo0djY3N2IifQ.90uebT4-ow1uqZKTUrf6RQ'))