ADS citation bot
====================
Informs you via E-Mail and/or [Twitter](https://twitter.com/AdsCitations) about new citations to your academic papers.

## What does it do?
When one of your papers receives a new citation on ADS, you can get an E-Mail with the following text:

> New citation to:
Optimized transit detection algorithm
by: Heller, René et al. - Transit least-squares survey (...)
[https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract](https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract)


If you add your Twitter account, you will be tweeted:

> [@hippke](https://twitter.com/hippke) Your paper "Optimized transit detection algorithm" 
was cited by Heller, René et al. - Transit least-squares survey (...) 
[https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract](https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract)

## How to register?
Register and manage your settings with this [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSejpaPLTVaI3KZZcgvPGBLwmkn26yMX5MpGwf9kQINzGC8Olw/viewform?vc=0&c=0&w=1&usp=mail_form_link) 
- If you want to receive Twitter tweets, follow [AdsCitations](https://twitter.com/AdsCitations).
- In the form, provide your ADS search string:
  - This is an ADS search which yields *the papers you have published*.
  - [For example](https://ui.adsabs.harvard.edu/search/q=%20author%3A%22hippke%2Cm.%22&sort=date%20desc%2C%20bibcode%20desc&p_=0): `author:hippke,m`
  - The bot will search for citations *to these papers*.
  - To create and test your query, open [ADS](https://ui.adsabs.harvard.edu/) and fiddle with the search until (ideally) all of your papers, but *only your papers*, are found.
  - People with a common name may try something like [this example](https://ui.adsabs.harvard.edu/search/q=author%3A(%22Heller%2C%20R%22)%20AND%20NOT%20author%3A%22Sarkar%2C%20S%22%20AND%20NOT%20author%3A%22Abdou%2C%20Y%22%20AND%20pubdate%3A%5B2009-01%20TO%209999-12%5D%20AND%20database%3Aastronomy%20AND%20property%3Arefereed&sort=date%20desc%2C%20bibcode%20desc&p_=0). Alternatively, assign an ORCiD to your papers and search for `orcid:XXX`. You can also search for [your bibcodes](https://ui.adsabs.harvard.edu/search/fl=identifier%2C%5Bcitations%5D%2Cabstract%2Caff%2Cauthor%2Cbibcode%2Ccitation_count%2Ccomment%2Cdoi%2Cid%2Ckeyword%2Cpage%2Cproperty%2Cpub%2Cpub_raw%2Cpubdate%2Cpubnote%2Cread_count%2Ctitle%2Cvolume%2Clinks_data%2Cesources%2Cdata%2Ccitation_count_norm%2Cemail%2Cdoctype&q=bibcode%3A(2019IJAsB..18..393H%20OR%202019AJ....158..143H)&rows=25&sort=date%20desc%2C%20bibcode%20desc&start=0&p_=0).
  - You need to insert the *search string from the ADS search box* into the registration form (*not the ADS URL from your browser*).

## Update mode
- After registration, you will receive an E-Mail (if you select E-Mail updates) with *all* citations found initially. Afterwards, the bot will search ADS *once per day* for *new* citations and send you an E-Mail *if and only if* you have received new citations.
- If you add your Twitter username, you will receive *up to three tweets per day* about new citations.

## Issues
- The information you provide (E-Mail, Twitter handle, ADS query) will be processed by Github Actions and become exposed to the public.
- Users with very many papers may be removed to avoid overload. The current limit is 200 papers.
- If you have any issues, please [open an issue on Github](https://github.com/hippke/adsbot/issues)
