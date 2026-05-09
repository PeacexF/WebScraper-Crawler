# Description

A Web Scraper + Crawler using python scrappy.

# Features
- requsts through proxy
- fuzzing
- crawling
- JSON & HTMl extraction

# Usage

Get a `wordlist.txt`, u can find lots and lots of wordlist for fuzzing on the internet. I reccomend [SecLists](https://github.com/danielmiessler/SecLists)  

Get a `raw_proxies.txt` I kinda have a proxy strainer that filters public proxies into usable ones in my other [repo](https://github.com/PeacexF/Proxy-Strainer), soo yeah, u can use that. First run `filter.py` to get rid of unneeded 'socks' types. 

Optional: update User Agents list in the code.

**Would not recommend runing it on your local machine**, unless you want to get yourself in all the blacklists of the world. I honestly am already in them, because of the auto-mailer I tested XD

It will not work properly without a list of good proxies, you will just endlessle get errors.

# License

MIT License