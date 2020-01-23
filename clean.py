from datetime import datetime

"""
Testfälle:
- Angemeldet
- an, ab
- an, an (identische Daten)
- an, an (teilmatch Daten)
- an, ab, an
- an, ab mit falschen Daten
- ab (ohne früheres an)
"""

subscribers = [
    ['23.01.2010 17:23:33', 'p1@abc.de', 'handle1', 'abs1'],
    ['24.01.2010 17:23:33', 'p2@abc.de', 'handle2', 'abs2'],
    ['25.01.2010 17:23:33', 'p3@abc.de', 'handle3', 'abs3'],
    ['26.01.2010 17:23:33', 'p4@abc.de', 'handle4', 'abs4'],
    ['27.01.2010 17:23:33', 'p5@abc.de', 'handle5', 'abs5'],
    ['28.01.2010 17:23:33', 'p6@abc.de', 'handle6', 'abs6'],
    ['29.01.2010 17:23:33', 'p2@abc.de', 'handle3', 'abs7'],
    ['30.01.2010 17:23:33', 'p8@abc.de', 'handle8', 'abs8'],
]

unsubscribers = [
    ['24.01.2010 17:23:33', 'p5@abc.de', 'handle11'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle12'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle13'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle14'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle15'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle16'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle17'],
    ['23.01.2010 17:23:33', 'test@abc.de', 'handle18'],
]


#a1 = '23.01.2010 17:23:33'
#a2 = '23.01.2019 17:21:21'
#date_object1 = datetime.strptime(a1, "%d.%m.%Y %H:%M:%S")
#print("date_object1 =", date_object1)
#date_object2 = datetime.strptime(a2, "%d.%m.%Y %H:%M:%S")
#print("date_object2 =", date_object2)
"""
if date_object1 < date_object2:
    print('Second date is later')
else:
    print('Second date is earlier')
"""


# Cleanse sub and unsub, e.g. remove @ from twitter entry

# Remove oldes entries from subscribers if duplicates exist
list_mails = []
list_twitters = []
for subscriber in reversed(subscribers):
    sub_mail = subscriber[1]
    sub_twitter = subscriber[2]
    if (sub_mail in list_mails) or (sub_twitter in list_twitters):
        subscriber[0] = ''
        subscriber[1] = ''
        subscriber[2] = ''
        subscriber[3] = ''
    list_mails.append(sub_mail)
    list_twitters.append(sub_twitter)



# Iterate over unsubscribers and delete them from list of subscribers
for unsubscriber in unsubscribers:
    unsub_date = unsubscriber[0]
    unsub_mail = unsubscriber[1]
    unsub_twitter = unsubscriber[2]
    for subscriber in subscribers:
        sub_date = subscriber[0]
        sub_mail = subscriber[1]
        sub_twitter = subscriber[2]
        #sub_query = subscriber[3]
        if (sub_mail == unsub_mail) or (sub_twitter == unsub_twitter):
            print('match', sub_mail, unsub_mail, sub_twitter, unsub_twitter)
            subscriber[0] = ''
            subscriber[1] = ''
            subscriber[2] = ''
            subscriber[3] = ''

for subscriber in subscribers:
    print(subscriber)

