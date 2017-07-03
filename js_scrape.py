import requests
'''
bibtex_id = '10.1007/s00425-007-0544-9'

url = "http://www.doi2bib.org/#/doi/{id}".format(id=bibtex_id)
xhr_url = 'http://www.doi2bib.org/doi2bib'

with requests.Session() as session:
    session.get(url)

    response = session.get(xhr_url, params={'id': bibtex_id})
    print(response.content)

'''
da_no = 'https://data.boston.gov/dataset'

with requests.Session() as session:
    session.get('https://data.boston.gov/dataset')

    response = session.get(da_no, params={'class': 'dataset_heading'})
    print(response.content)

