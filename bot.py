import smtplib
import codecs
import os.path
import os
import ads
from twython import Twython
from email.mime.text import MIMEText


# CONSTANTS
filename_participants = 'participants.csv'
delimiter = '|'
folder = "data/"
ads.config.token = os.environ.get('SECRET_ADS_CONFIG_TOKEN')

# Twitter
chars_total_max = 280  # Twitter tweets are at most 280 chars
chars_title_my_paper_max = 50
chars_author_citing_paper_max = 50
chars_ADS_url = 53
max_tweets_per_user = 3

# E-Mail
smtp_server = 'smtp.hippke.org'
mail_from = 'adsbot@hippke.org'
smtp_port = '587'


def shorten_string(string, chars=40, separators=[':', ' - ', '?', '. ', '—'], continuation=' (...)'):

    # Split by separators
    if len(string) > (chars-len(continuation)):
        for separator in separators:
            string = string.split(separator, 1)[0]
            if len(string) < (chars-len(continuation)):
                string = string + continuation
                break

    # Split by space next closest (leftwards) from maximum chars
    if len(string) > (chars-len(continuation)):
        string = string[:chars-len(continuation)]
        pos = string.rindex(' ')
        string = string[:pos] + continuation
    return string


def check_if_new_citations(filename, query):
    if not os.path.isfile(filename):
        filehandle = open(filename, "w")  # Append
        filehandle.close()
    filehandle = open(filename, "r")
    known_citing_papers = [line.rstrip('\n') for line in filehandle]
    filehandle = open(filename, "a")
    new_paper_found = False
    search_string = "citations(" + query + ")"
    print('Running ADS with query', search_string)
    #try:
    citing_papers = ads.SearchQuery(q=search_string, sort="date")  # , rows=20)
    print('Query completed')
    #except:
    #    print('Error in ADS query')
    #    return new_paper_found
    print('Query completed, after try..except block')
    for citing_paper in citing_papers:
        print(citing_paper.bibcode)
        if citing_paper.bibcode not in known_citing_papers:
            print('New paper found!', citing_paper.bibcode)
            new_paper_found = True
            break
    print(citing_papers.response.get_ratelimits())
    return new_paper_found


def get_new_citations(filename, query):
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
        Text which describes new citations. If empty, no new citations were found.
    """
    counter_new_papers = 0
    mailtext = []
    tweets = []
    # File which holds list of bibcodes with known citing papers, each in a new line
    if not os.path.isfile(filename):
        filehandle = open(filename, "w")  # Append
        filehandle.close()
    filehandle = open(filename, "r")
    known_citing_papers = [line.rstrip('\n') for line in filehandle]
    filehandle = open(filename, "a")
    lazy_evaluation = ['bibcode', 'title', 'author', 'citation_count']
    my_papers = ads.SearchQuery(q=query, sort='citation_count', fl=lazy_evaluation)
    print('Papers by', query)
    for paper in my_papers:
        citing_papers = ads.SearchQuery(
            q="citations(bibcode:" + paper.bibcode + ")",
            sort="date",
            fl=lazy_evaluation
            )
        for citing_paper in citing_papers:
            if paper.citation_count > 0 and citing_paper.bibcode not in known_citing_papers:
                known_citing_papers.append(citing_paper.bibcode)
                counter_new_papers +=1
                text = 'New citation to:\n' + paper.title[0] + '\nby: ' + \
                    citing_paper.author[0] + " - " + \
                    citing_paper.title[0] + "\n" + \
                    'https://ui.adsabs.harvard.edu/abs/' + str(citing_paper.bibcode) + "\n"
                print(text)
                mailtext.append(text)
                filehandle.writelines(citing_paper.bibcode+ '\n')
                
                # Twitter string
                tweet = '@' + twitter_username + ' Your paper \"' + \
                    shorten_string(paper.title[0], chars=chars_title_my_paper_max) + \
                    '\" was cited by ' + \
                    shorten_string(citing_paper.author[0], chars=chars_author_citing_paper_max) + ': '
                remaining_chars = chars_total_max - len(tweet)
                tweet = tweet + shorten_string(citing_paper.title[0], chars=remaining_chars-chars_ADS_url)
                tweet = tweet + ' https://ui.adsabs.harvard.edu/abs/' + str(citing_paper.bibcode)
                tweets.append(tweet)
                print('tweet:', tweet)
            else:
                print(citing_paper.bibcode, 'no new citations')
    print(citing_papers.response.get_ratelimits())
    print('new papers:', counter_new_papers)
    filehandle.close()
    return mailtext, tweets


def send_mail(mailtext, address_to):
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.login(mail_from, os.environ.get('SECRET_MAIL_PASSWORD'))
    msg = MIMEText('\n'.join(mailtext))
    msg['Subject'] =  "ADS bot: New citations"
    msg['From'] = mail_from
    msg['To'] = address_to
    server.sendmail(mail_from, address_to, msg.as_string())


file = open(filename_participants, "r")
twitter = Twython(
    os.environ.get('consumer_key'),
    os.environ.get('consumer_secret'),
    os.environ.get('access_token'),
    os.environ.get('access_token_secret')
    )
for line in file:
    adr = line.split(delimiter)[0]
    twitter_username = line.split(delimiter)[1]
    query = line.split(delimiter)[2].rstrip()
    
    # Quick check if new papers are found for this query
    new_paper_found = check_if_new_citations(folder + adr, query)
    
    # If yes, iter over all papers of this author to check WHICH papers are cited
    if new_paper_found:
        print('New paper(s) found for', adr)
        mailtext, tweets = get_new_citations(folder + adr, query)
        
        # Send E-Mail
        if adr == '':
            print('No email address provided, skipping email')
        else:
            print('Sending mail to', adr)
            send_mail(mailtext, adr)
            print('Mail sent.')
            
        # Send Twitter tweet
        if twitter_username == '':
            print('No twitter_username provided, skipping twitter', twitter_username)
        else:
            print('Twitter_username provided, tweeting to:', twitter_username)
            counter = 0
            for idx in range(len(tweets)):
                if counter >= max_tweets_per_user:
                    print('Maximum number of tweets reached, aborting:', max_tweets_per_user)
                    break
                print('Tweeting tweet:', tweets[idx])
                #twitter.update_status(status=tweets[idx])
                counter += 1
    else:
        print('No new paper found for', adr)
print('End of script.')
