ADS citation bot
====================
Informs you via E-Mail and/or [Twitter](https://twitter.com/AdsCitations) about new citations to your academic papers.

## What does it do?
When one of your papers receives a new citation on ADS, you will get an E-Mail with the following text:

> New citation to:
Optimized transit detection algorithm
by: Heller, René et al. - Transit least-squares survey (...)
[https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract](https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract)


If you have registered with your Twitter account, you will be tweeted:

> [@hippke](https://twitter.com/hippke) Your paper "Optimized transit detection algorithm" 
was cited by Heller, René et al. - Transit least-squares survey (...) 
[https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract](https://ui.adsabs.harvard.edu/abs/2019A%26A...627A..66H/abstract)

## How to register?
Register by filling out [this form](https://docs.google.com/forms/d/e/1FAIpQLSejpaPLTVaI3KZZcgvPGBLwmkn26yMX5MpGwf9kQINzGC8Olw/viewform?vc=0&c=0&w=1) (or unsubscribe with [this form](https://docs.google.com/forms/d/e/1FAIpQLScYMA3eXCcZ0J2GF7DwLSFKfWPnqBkQ6vrkYWm9dHk0sD5-Pw/viewform?vc=0&c=0&w=1&usp=mail_form_link)):
- Provide E-Mail and/or Twitter (but at least one). If you want to receive Twitter tweets, follow [AdsCitations](https://twitter.com/AdsCitations).
- Provide your ADS search string:
  - This is an ADS search which yields *the papers you have published*.
  - [For example](https://ui.adsabs.harvard.edu/search/q=%20author%3A%22hippke%2Cm.%22&sort=date%20desc%2C%20bibcode%20desc&p_=0): `author:hippke,m.`
  - The bot will search for citations *to these papers*.
  - To create and test your query, open [ADS](https://ui.adsabs.harvard.edu/) and fiddle with the search until (ideally) all of your papers, but *only your papers*, are found.
  - People with a common name may try something like [this example](https://ui.adsabs.harvard.edu/search/q=author%3A(%22Heller%2C%20R%22)%20AND%20NOT%20author%3A%22Sarkar%2C%20S%22%20AND%20NOT%20author%3A%22Abdou%2C%20Y%22%20AND%20pubdate%3A%5B2009-01%20TO%209999-12%5D%20AND%20database%3Aastronomy%20AND%20property%3Arefereed&sort=date%20desc%2C%20bibcode%20desc&p_=0).
  - You need to insert the search string (from the ADS search box) into the registration form (*not the ADS URL from your browser*).

Currently, this bot in in beta testing mode. Adding new users may take several days. Please be patient.

## Next steps
- After registration, you will receive an E-Mail (if you provided one) with *all* citations found initially. Afterwards, the bot will search ADS *once per day* for *new* citations and send you an E-Mail *if and only if* you have received new citations.
- If you added your Twitter username, you will receive *up to three tweets per day* about new citations.
- If you like to change your ADS query, please unsubscribe and re-subscribe
