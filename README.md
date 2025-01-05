# vcalendar2ics
## aim
format converter from vcalencar format to ics format.

## how I made
I asked ChatGPT-4o to make the converter in order to keep the data on docomo schedule and memo when I changed the smart phone.</br> 
And after I checked the output file I asked the additional modification of the converter.</br>
I referred https://qiita.com/S_Kosaka/items/bcc1f18ab6aab20bd807 in order to know the format.

## program
vcalendar2ics.py : main program

## issues
- Every event is separated to the different files because the import errors to the google calendare sometimes occur. 
- If \n contains in summary, google calendar may fail the import.
