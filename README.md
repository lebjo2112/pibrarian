# pibrarian

## Installation


`git clone https://github.com/lebjo2112/pibrarian.git`

`cd pibrarian`

`pip3 install -r requirements.txt`

## Usage
Pibrarian only runs on Linux, as it was meant to be run on a raspberry pi, however with a few small adjustments it should be able to run on any system without issue.
Pibrarian is a drive catalog script that stores file location information in an sql database. 
After cataloging a drive's contents, pibrarian pulls data from IMDB for appropriate media.

to run:

`python3 pibrarian.py`

## Goals
Currently pibrarian is only able to pull information regarding Movies and Television shows, and it is not 100% accurate with all titles.
With that in mind, I would like to improve accuracy, as well as extract data for music artists and authors.
I would like it to be able to make suggesstions based on recently consumed media, based on similarity of content or people involved in a specific project.
Since Pibrarian is a backup management tool, it should be able to compile, and actively, separate sources to interact with Kodi, PLEX, and similar services.
ie. On December 1st, make a collection of christmas movies avaliable to stream on local network, or Horror films for halloween, etc. 
Clearly there's lots to be done on this.
