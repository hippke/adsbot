import requests
from email_validator import validate_email, EmailNotValidError

filename_participants = 'participants.csv'
unsubscriber_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDroFrqsXekEfCz0RnzTLAqfsopYbvfwMBO94_STcGrylKbxkKFb1QF1bTfzjg3ey2DjnKONg2R3Eg/pub?gid=964923441&single=true&output=tsv"
subscribers_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpe5VMgz4cklREQ2wyVib6EbF05VXdptqg1tQrNNaRYq3sAEGZSsdIiNOz5LS-koRANbMRad2jsEYU/pub?gid=89736868&single=true&output=tsv"
subscribers_data = requests.get(subscribers_url)


def fetch_data(url):
    data = requests.get(url)
    lines = str(data.text).splitlines()
    # Drop first line which holds the column names
    lines.pop(0)
    result = []
    for line in lines:
        date = line.split("\t")[0]
        mail = line.split("\t")[1]
        twitter = line.split("\t")[2]
        try:
            query = line.split("\t")[3]
            result.append([date, mail, twitter, query])
        except:
            result.append([date, mail, twitter])
    return result


def twitter_validation(username):
    if username != '':
        # max 15 chars
        if len(username) > 15:
            print('Twitter username invalid, too long', len(username), username)
            return ''
        # remove initial @ if given
        if username[0] == '@':
            return username[1:]
    return username


def email_validation(mail):
    try:
        validate_email(mail)
        return mail
    except EmailNotValidError:
        print('Mail purged:', mail)
        return ''


# Data cleansing
subs = fetch_data(subscribers_url)
for sub in subs:
    sub[1] = email_validation(sub[1])
    sub[2] = twitter_validation(sub[2])
    # Remove ADS entry if NONE OF MAIL OR TWITTER REMAIN
    if sub[1] == '' and sub[2] == '':
        sub[3] = ''

#for line in subs:
#    print(line)
#print(' ')

# No ADS to remove; just Mail and/or Twitter
unsubs = fetch_data(unsubscriber_url)
for unsub in unsubs:
    unsub[1] = email_validation(unsub[1])
    unsub[2] = twitter_validation(unsub[2])

# Remove oldes entries from subscribers if duplicates exist
list_mails = []
list_twitters = []
for subscriber in reversed(subs):
    sub_mail = subscriber[1]
    sub_twitter = subscriber[2]
    if (sub_mail in list_mails) or (sub_twitter in list_twitters):
        subscriber[0] = ''
        subscriber[1] = ''
        subscriber[2] = ''
        subscriber[3] = ''
    list_mails.append(sub_mail)
    list_twitters.append(sub_twitter)

#for line in subs:
#    print(line)
#print(' ')

# Iterate over unsubscribers and delete them from list of subscribers
for unsubscriber in unsubs:
    unsub_date = unsubscriber[0]
    unsub_mail = unsubscriber[1]
    unsub_twitter = unsubscriber[2]
    for subscriber in subs:
        sub_date = subscriber[0]
        sub_mail = subscriber[1]
        sub_twitter = subscriber[2]
        if (sub_mail == unsub_mail) or (sub_twitter == unsub_twitter):
            #print(sub_mail, unsub_mail)
            if sub_date < unsub_date:
                subscriber[0] = ''
                subscriber[1] = ''
                subscriber[2] = ''
                subscriber[3] = ''

#for line in subs:
#    print(line)
#print(' ')

# Drop empty lines
filehandle = open(filename_participants, "w")
for idx in range(len(subs)):
    if ''.join(subs[idx]) is not '':
        # Drop date, add separator
        participant = '|'.join(subs[idx][1:])
        print(participant)
        filehandle.writelines(participant + '\n')
