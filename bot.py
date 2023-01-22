import os
import ads
import requests
import hashlib
from urllib.parse import unquote


# CONSTANTS
subscribers_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTr1cqBIet6x-04q1TPVboWi9IgPGfemIovBrWcRk5tEqhFhNQ5Zrfvb8Lkq4qWam5AXPhq9kSRjffA/pub?gid=208468094&single=true&output=tsv"
ads.config.token = os.environ.get("ads_config_token")
path_mails = "mails/"
folder = "data/"
error_mail = "michael@jaekle.info"  # Prepare mail if error occurs

# Twitter
path_tweets = "tweets/"
chars_total_max = 280  # Twitter tweets are at most 280 chars
chars_title_my_paper_max = 50
chars_author_citing_paper_max = 50
chars_ADS_url = 53
max_tweets_per_user = 20


def shorten_string(
    string, chars=40, separators=[":", " - ", "?", ". ", "—"], continuation=" (...)"
):
    """Shorten Twitter tweet strings gracefully after separators or word endings"""
    # Split by separators
    if len(string) > (chars - len(continuation)):
        for separator in separators:
            string = string.split(separator, 1)[0]
            if len(string) < (chars - len(continuation)):
                string = string + continuation
                break

    # Split by space next closest (leftwards) from maximum chars
    if len(string) > (chars - len(continuation)):
        string = string[: chars - len(continuation)]
        pos = string.rindex(" ")
        string = string[:pos] + continuation
    return string


def safe_ads_query(query):
    """If user provides URL instead of query, return only the query"""
    if query.startswith("http"):
        try:
            query = unquote(unquote(query))
            query = query.split("ui.adsabs.harvard.edu/search/q=", 1)[1]
            query = query.split("&", 1)[0]  # Before the first & which indicates sorting
            return query
        except:
            print("URL conversion failed, preparing mail to", error_mail)
            if not os.path.exists(path_mails):
                os.makedirs(path_mails)
            output_filename = error_mail  # Mail address is filename
            filehandle = open(path_mails+output_filename, "w")
            filehandle.writelines("URL query conversion failed:" + query)
            filehandle.close()
            print('Created', path_mails+output_filename)
            return ""
    else:
        return query


def ads_check(filename, query):
    if not os.path.isfile(filename):
        f = open(filename, "w")
        f.close()
    f = open(filename, "r")
    known_citing_papers = [line.rstrip("\n") for line in f]
    f = open(filename, "a")
    print("Running ADS with query", query)
    papers = ads.SearchQuery(q=query, rows=2000, fl=["bibcode", "citation", "title"])
    papers.execute()
    print("Requests remaining:", papers.response.get_ratelimits()["remaining"])
    counter = 0
    try:
        counter_max = int(papers.response.get_ratelimits()["remaining"]) - 500
    except:
        counter_max = 25000
    new_cits = []
    for paper in papers:
        if paper.citation is not None:
            for cit in paper.citation:
                if cit not in known_citing_papers:
                    print("    new cit to", paper.bibcode, "by", cit)
                    counter += 1
                    if counter > counter_max:
                        break
                    f.writelines(cit + "\n")
                    # This is a new citing paper. We want its title and authors
                    citing_papers = ads.SearchQuery(q="bibcode:"+cit)
                    for citing_paper in citing_papers:
                        new_cits.append(
                            [
                                paper.title[0],
                                citing_paper.author,
                                citing_paper.title[0],
                                citing_paper.bibcode,
                            ]
                        )
    f.close()
    return new_cits


def compose_tweet(
    twitter_username,
    paper_title,
    citing_paper_author,
    citing_paper_title,
    citing_paper_bibcode,
):
    """Example:
    tweet: @hippke Your paper "Photometry’s Bright Future (...)" 
    was cited by Angerhausen, Daniel et al.: 
    A Comprehensive Study of Kepler Phase Curves and Secondary Eclipses (...) 
    https://ui.adsabs.harvard.edu/abs/2015PASP..127.1113A
    """
    if citing_paper_author is None:
        return ""
    else:
        if len(citing_paper_author) > 1:
            text_et_al = " et al."
        else:
            text_et_al = ""
    tweet = (
        "@"
        + twitter_username
        + ' Your paper "'
        + shorten_string(paper_title, chars=chars_title_my_paper_max)
        + '" was cited by '
        + shorten_string(citing_paper_author[0], chars=chars_author_citing_paper_max)
        + text_et_al
        + ": "
    )
    # Calculate remaining chars (max 280) and fit in the citing paper and its URL
    remaining_chars = chars_total_max - len(tweet)
    tweet = tweet + shorten_string(
        citing_paper_title, chars=remaining_chars - chars_ADS_url
    )
    tweet = tweet + " https://ui.adsabs.harvard.edu/abs/" + citing_paper_bibcode
    return tweet


def compose_mail_segment(
    paper_title, citing_paper_author, citing_paper_title, citing_paper_bibcode
):
    """Example:
    New citation to:
    Photometry’s Bright Future: Detecting Solar System Analogs with Future Space Telescopes
    by: Angerhausen, Daniel et al. - A Comprehensive Study of Kepler Phase Curves and 
    Secondary Eclipses: Temperatures and Albedos of Confirmed Kepler Giant Planets
    https://ui.adsabs.harvard.edu/abs/2015PASP..127.1113A
    """

    if citing_paper_author is None:
        return ""
    else:
        if len(citing_paper_author) > 1:
            text_et_al = " et al."
        else:
            text_et_al = ""

    text = (
        "New citation to:\n"
        + paper_title
        + "\nby: "
        + citing_paper_author[0]
        + text_et_al
        + " - "
        + citing_paper_title
        + "\n"
        + "https://ui.adsabs.harvard.edu/abs/"
        + citing_paper_bibcode
        + "\n\n"
    )
    return text


def get_subscribers(subscribers_url):
    subscribers = iter(requests.get(subscribers_url).text.splitlines())
    next(subscribers)  # Skip first row which holds the headers
    subs = []
    for line in subscribers:
        mail, send_mail, twitter_name, send_tweet, query = line.split("\t")[1:6]

        if send_mail == "Yes":
            send_mail = True
        else:
            send_mail = False

        if send_tweet == "Yes":
            send_tweet = True
        else:
            send_tweet = False

        subs.append([mail, send_mail, twitter_name, send_tweet, query])
    return subs


def run_bot():
    print("Subscribers:")
    subs = get_subscribers(subscribers_url)
    try:
        for sub in subs:
            mail, send_mail, twitter_name, send_tweet, query = sub
            print(mail, send_mail, twitter_name, send_tweet, query)

            # Some users provide the ADS URL instead of the search string
            # Try to convert. If that failes, send a mail error to me (for now)
            # It this will be a common problem, consider mailing the user directly
            query = safe_ads_query(query)
            #try:
            new_cits = ads_check(folder+mail, query)
            tweets = []
            mailtext = []
            for cit in new_cits:
                paper_title, citing_paper_author, citing_paper_title, citing_paper_bibcode = cit
                # Twitter tweet
                tweet = compose_tweet(
                    twitter_name,
                    paper_title,
                    citing_paper_author,
                    citing_paper_title,
                    citing_paper_bibcode,
                    )
                tweets.append(tweet)
                print("tweet:", tweet)
                print("")

                # Mail segment
                mailtext_segment = compose_mail_segment(
                    paper_title,
                    citing_paper_author,
                    citing_paper_title,
                    citing_paper_bibcode,
                )
                mailtext.append(mailtext_segment)
                print(mailtext_segment)

            # Save E-Mail
            if send_mail:
                if mailtext != []:
                    print("Saving mail to", mail)
                    if not os.path.exists(path_mails):
                        os.makedirs(path_mails)
                    output_filename = mail  # Mail address is filename
                    filehandle = open(path_mails+output_filename, "w")
                    filehandle.writelines(mailtext)
                    filehandle.close()
                    #print('Created', path_mails+output_filename)
                    #print("Mail saved")
                else:
                    print("No mail")
            #else:
            #    print("No email address provided, skipping email")

            # Save Twitter tweet
            if send_tweet:
                #print("Twitter_username provided, creating tweets for:", twitter_name)
                if not os.path.exists(path_tweets):
                    os.makedirs(path_tweets)
                for idx in range(len(tweets)):
                    if idx >= max_tweets_per_user:
                        print("max_tweets_per_user, aborting:", max_tweets_per_user)
                        break
                    output_filename = hashlib.md5(tweets[idx].encode('utf-8')).hexdigest()
                    filehandle = open(path_tweets+output_filename, "w")
                    filehandle.writelines(tweets[idx])
                    filehandle.close()
                    print('Tweet created', path_tweets+output_filename, tweets[idx])
    except:
        print('Failed for this sub')

if __name__ == "__main__":
    run_bot()
