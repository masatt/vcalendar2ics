# vcalendar2ics
## aim
format converter from vcalencar format to ics format.

## how I made
I asked ChatGPT-4o to make the converter in order to keep the data on docomo schedule and memo when I changed the smart phone. 
And after I checked the output file I asked the additional modification of the converter.

## program
vcalendar2ics.py : main program

## issues
Every event is separated to the different files because the import errors to the google calendare sometimes occur. 
If \n contains in summary, google calendar may fail the import.
