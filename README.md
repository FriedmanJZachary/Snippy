# Snippy-s-Word-of-the-Day
A word-of-the-day emailer that scrapes various websites for word pronunciations, etymologies, etc. and emails this information daily. It generates HTML code on the fly to format these emails and maintains a full-fledged user database using MySQL that is modified through a user-accessible Flask website.

This project utilizes the following services:

-Etymonline
-Flask
-Merriam-Webster Dictionary API
-MySQL
-NoIP (for hostname designation)
-NY Times Word of the Day
-open-dict-data (IPA Lookup)

While the full implementation of this project can be somewhat involved, a simple, single-file version of the project can be found as simple.py, which requires input of a desired word and email address(es) into the file. The primary implementation can be found as wotd.py, which relies on wordList.txt, rather than the NY Times, for new words. The NY Times version can be found as NYTimes.py. Note that both pof these latter versions require MySQL setup.
