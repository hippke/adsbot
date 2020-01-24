def valid_query(query, threshold=200):
    """Checks ADS query if valid and if number of papers < threshold"""

    papers = ads.SearchQuery(q=query, rows=threshold+1)
    counter = 0
    try:
        for paper in papers:
            counter += 1
    except:
        print('Invalid ADS query')
        return False
    print(papers.response.get_ratelimits())
    print('Papers:', counter)
    if counter <= threshold:
        return True
    else:
        return False
