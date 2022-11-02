I created 2 files, first one main.py is just crawling script that is not even saving to csv/json.

First file You can start in termianl with command -> python main.py "link"

After you run this script its gonna take a minute or two and script gonna start printing titles with internal and external links, we have to wait as long as we gonna get big dict() with internal links. 

Second file second_main.py is crawling with asyncio and saving to file json / csv.
Second file You can start by typing in terminal -> python second_main.py 
You don't have to put link or --file csv/json in the second file couse url is static set to https://crawler-test.com/ 


After srcipt end working you gonna get 3 files.
Crawler.json, Crawler.csv and Crawler.txt
