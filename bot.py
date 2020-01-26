import smtplib
import codecs
import datetime
import os.path
import os
import ads
import requests
from twython import Twython
from email.mime.text import MIMEText


# CONSTANTS
subscribers_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTr1cqBIet6x-04q1TPVboWi9IgPGfemIovBrWcRk5tEqhFhNQ5Zrfvb8Lkq4qWam5AXPhq9kSRjffA/pub?gid=208468094&single=true&output=tsv"
folder = "data/"
max_papers_per_user = 200
ads.config.token = 'kcy1toBYw40EuNrTGzJC65IZ4kz3U0zJ4FiW9oU4'

# Twitter
chars_total_max = 280  # Twitter tweets are at most 280 chars
chars_title_my_paper_max = 50
chars_author_citing_paper_max = 50
chars_ADS_url = 53
max_tweets_per_user = 3
twitter = Twython(
    os.environ.get("consumer_key"),
    os.environ.get("consumer_secret"),
    os.environ.get("access_token"),
    os.environ.get("access_token_secret"),
)

# E-Mail
smtp_server = "smtp.hippke.org"
mail_from = "adsbot@hippke.org"
smtp_port = "587"


def shorten_string(
    string, chars=40, separators=[":", " - ", "?", ". ", "—"], continuation=" (...)"
):

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


def check_if_new_citations(filename, query):
    if not os.path.isfile(filename):
        filehandle = open(filename, "w")
        filehandle.close()
    filehandle = open(filename, "r")
    known_citing_papers = [line.rstrip("\n") for line in filehandle]
    filehandle = open(filename, "a")  # append
    new_paper_found = False
    search_string = "citations(" + query + ")"
    print("Running ADS with query", search_string)
    try:
        citing_papers = ads.SearchQuery(q=search_string, sort="date", rows=2000)
        citing_papers.execute()
    except:
        print("Error in ADS query")
        return False
    counter = 0
    for citing_paper in citing_papers:
        # print(citing_paper.bibcode)
        counter += 1
        if citing_paper.bibcode not in known_citing_papers:
            print("New paper found!", citing_paper.bibcode)
            new_paper_found = True
    if counter > max_papers_per_user:
        print(
            "Error: Too many papers for this user:",
            counter,
            "threshold:",
            max_papers_per_user,
        )
        new_paper_found = False
    wait_until = datetime.datetime.utcfromtimestamp(
        int(citing_papers.response.get_ratelimits()["reset"])
    )
    print(
        "Requests remaining:",
        citing_papers.response.get_ratelimits()["remaining"],
        "Reset in (hrs):",
        round((wait_until - datetime.datetime.now()).seconds / (3600), 1),
    )
    return new_paper_found


def compose_tweet(
        twitter_username,
        paper_title,
        citing_paper_author,
        citing_paper_title,
        citing_paper_bibcode
    ):
    """Example:
    tweet: @hippke Your paper "Photometry’s Bright Future (...)" 
    was cited by Angerhausen, Daniel et al.: 
    A Comprehensive Study of Kepler Phase Curves and Secondary Eclipses (...) 
    https://ui.adsabs.harvard.edu/abs/2015PASP..127.1113A
    """
    
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
        + shorten_string(
            citing_paper_author[0], chars=chars_author_citing_paper_max
        )
        + text_et_al
        + ": "
    )
    # Calculate remaining chars (max 280) and fit in the citing paper and its URL
    remaining_chars = chars_total_max - len(tweet)
    tweet = tweet + shorten_string(
        citing_paper_title, chars=remaining_chars - chars_ADS_url
    )
    tweet = (
        tweet
        + " https://ui.adsabs.harvard.edu/abs/"
        + citing_paper_bibcode
    )
    return tweet


def compose_mail_segment(
    paper_title,
    citing_paper_author,
    citing_paper_title,
    citing_paper_bibcode
):
    """Example:
    New citation to:
    Photometry’s Bright Future: Detecting Solar System Analogs with Future Space Telescopes
    by: Angerhausen, Daniel et al. - A Comprehensive Study of Kepler Phase Curves and 
    Secondary Eclipses: Temperatures and Albedos of Confirmed Kepler Giant Planets
    https://ui.adsabs.harvard.edu/abs/2015PASP..127.1113A
    """

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
        + "\n"
    )
    return text


def get_new_citations(filename, query, twitter_username):
    """
    Searches ADS with 'query'. In each paper with >0 citations, it pulls the citations.
    If a citation is not in 'filename', it is added to the returned text.
    Can't use query 'citations(hippke)' because that doesn't give the origin of the cit. 
    Parameters
    ----------    
    query : string
        ADS search query which returns papers of author.
        These are used to search for new citations to them.
    Returns
    -------
    mailtext : List of strings
        Text which describes new citations. Empty if no new citations.
    tweets : List of strings
        Tweeter tweets composed of new citations. Empty if no new citations.
    """
    counter_new_papers = 0
    mailtext = []
    tweets = []
    # File which holds list of bibcodes with known citing papers, each in a new line
    if not os.path.isfile(filename):
        filehandle = open(filename, "w")  # Append
        filehandle.close()
    filehandle = open(filename, "r")
    known_citing_papers = [line.rstrip("\n") for line in filehandle]
    filehandle = open(filename, "a")
    lazy_evaluation = ["bibcode", "title", "author", "citation_count"]
    my_papers = ads.SearchQuery(q=query, sort="citation_count", fl=lazy_evaluation)
    print("Papers by", query)
    for paper in my_papers:
        citing_papers = ads.SearchQuery(
            q="citations(bibcode:" + paper.bibcode + ")",
            sort="date",
            fl=lazy_evaluation,
        )
        for citing_paper in citing_papers:
            if (
                paper.citation_count > 0
                and citing_paper.bibcode not in known_citing_papers
            ):
                counter_new_papers += 1

                # Add to list of known citing bibcodes
                known_citing_papers.append(citing_paper.bibcode)
                filehandle.writelines(citing_paper.bibcode + "\n")

                # Mail segment
                mailtext_segment = compose_mail_segment(
                    paper.title[0],
                    citing_paper.author,
                    citing_paper.title[0],
                    str(citing_paper.bibcode)
                    )
                mailtext.append(mailtext_segment)
                print('Mail segment:', mailtext_segment)

                # Twitter tweet
                tweet = compose_tweet(
                    twitter_username,
                    paper.title[0],
                    citing_paper.author,
                    citing_paper.title[0],
                    str(citing_paper.bibcode)
                    )
                tweets.append(tweet)
                print("tweet:", tweet)
            else:
                print(citing_paper.bibcode, "no new citations")

    wait_until = datetime.datetime.utcfromtimestamp(
        int(citing_papers.response.get_ratelimits()["reset"])
    )
    print(
        "Requests remaining:",
        citing_papers.response.get_ratelimits()["remaining"],
        "Reset in (hrs):",
        round((wait_until - datetime.datetime.now()).seconds / (3600), 1),
    )

    print("new papers:", counter_new_papers)
    filehandle.close()
    return mailtext, tweets


def send_mail_func(mailtext_content, adr):
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.login(mail_from, os.environ.get("SECRET_MAIL_PASSWORD"))
    msg = MIMEText("\n".join(mailtext))
    msg["Subject"] = "ADS bot: New citations"
    msg["From"] = mail_from
    msg["To"] = adr
    server.sendmail(mail_from, adr, msg.as_string())


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
    for sub in subs:
        mail, send_mail, twitter_name, send_tweet, query = sub
        print(mail, send_mail, twitter_name, send_tweet, query)

        # Quick check if new papers are found for this query
        new_paper_found = check_if_new_citations(folder + mail, query)

        # If yes, iter over all papers of this author to check WHICH papers are cited
        if new_paper_found:
            print("New paper(s) found for", mail)
            mailtext, tweets = get_new_citations(folder + mail, query, twitter_name)

            # Send E-Mail
            if send_mail:
                if mailtext != []:
                    print("Sending mail to", mail)
                    send_mail_func(mailtext, mail)
                    print("Mail sent.")
                else:
                    print("Empty mailtext, should be something here!")
            else:
                print("No email address provided, skipping email")

            # Send Twitter tweet
            if send_tweet:
                print("Twitter_username provided, tweeting to:", twitter_name)
                counter = 0
                for idx in range(len(tweets)):
                    if counter >= max_tweets_per_user:
                        print(
                            "Maximum number of tweets reached, aborting:",
                            max_tweets_per_user,
                        )
                        break
                    print("Tweeting tweet:", tweets[idx])
                    twitter.update_status(status=tweets[idx])
                    counter += 1

            else:
                print("No twitter_username provided, skipping twitter", twitter_name)
        else:
            print("No new paper found for", mail)
    print("End of script.")


if __name__ == '__main__':
    run_bot()
