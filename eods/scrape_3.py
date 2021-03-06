import bs4
import numpy as np
import pandas as pd
import re
import urllib3


def make_one_column(datasets, name):
    a = pd.concat([pd.Series(d).drop_duplicates() for d in datasets]).to_frame().rename(columns={0:name}).reset_index(drop=True)
    return a

def get_soup(url):
        pm = urllib3.PoolManager()
        def make_html(pm,url):
            return pm.urlopen(url= url, method="GET").data
        return bs4.BeautifulSoup(make_html(pm,url), 'html.parser')
class Place(object):

    def __init__(self, input_dict):

        self.loc = input_dict['Location']
        self.state = input_dict['State']
        self.pop = input_dict['Population (US Census, 2011)']
        self.ownership = input_dict['Ownership?']
        self.policy = input_dict['Open Data Policy?']
        self.link = input_dict['Link']
        self.type = input_dict['Type']
        self.all_results = None

        self.datasets = None

        self._get_info()

    @property
    def shortlink(self):

        return self.link.lstrip('htps').lstrip(':/').rstrip('/')

    @property
    def name(self):

        return '{0} ({1})'.format(self.loc, self.shortlink)

    @property
    def _link_to_try(self):

        link = (self.link if self.link[-1] == '/' else self.link + '/')

        return link + 'browse?sortBy=most_accessed'

    @property
    def __repr__(self):
        return '<%s, %s ,%s, %s, %s, %s, %s>' % (
    self.loc, self.state, self.pop,
    self.ownership, self.policy, self.link, self.type)


    @property
    def __repr_data__(self):
        return'%s' %(self.datasets)

    def _get_info(self):
        print('getting info')
        try:
            s = self._get_soup(self.link+'/browse')
        except:
            return
        #else:
        soc = self._is_socrata
        if soc:
            print('Starting: ' + self.name)
            self.datasets = pd.DataFrame()
            for res in self._read_page(s):
                self._parse_result(res)
            if self.link[-1] == '/':
                self.link = self.link+'browse'
            else:
                self.link = self.link+'/browse'
            self.datasets['topics'] = self._get_tag_info('a', 'name-link', topic=True)
            print('Completed: ' + self.name)
     
    
    def _read_all_pages(self):

        pattern_ev = r'.+(?=/browse)'

        soup = self._get_soup(self.link)

        try:

            return [re.findall(pattern_ev, self.link)[0]+x['href'] for x in soup.find_all('a','pageLink') if x['href']]

        except:

            return [self.link+x['href'] for x in soup.find_all('a','pageLink') if x['href']]
    
    def _get_tag_info(self, tag_type, class_end, topic = False):

        if not self.all_results:
            return None

        if topic == True:

            data = [[x['href'] for x in get_soup(results).find_all(tag_type,'browse2-result-'+class_end) if x['href']] for results in self.all_results]
        else:
            data = [[x.text for x in get_soup(results).find_all(tag_type,'browse2-result-'+class_end) if x.text] for results in self.all_results]
        #print(self.name)
        return make_one_column(data, class_end)

    @staticmethod
    def _get_soup(url):
        pm = urllib3.PoolManager()
        def make_html(pm,url):
            return pm.urlopen(url= url, method="GET").data
        return bs4.BeautifulSoup(make_html(pm,url), 'html.parser')

    @staticmethod
    def _is_socrata(page_soup):

        def _is_comment(x): 
            print('check comment')
            return isinstance(x, bs4.Comment)

        print('checking socrata')

        comments = page_soup.find_all(text=_is_comment)

        if ('Powered by the Socrata Open Data Platform' in str(comments)):
            return True
        else:
            return False

    @staticmethod
    def _read_page(page_soup):

        return page_soup.find_all('div', {'class': 'browse2-result'})

    def _parse_result(self, result):

        def _find(child_tag_type, class_):

            child_tag = result.find(child_tag_type,
                                    {'class': 'browse2-result-' + class_})
            if child_tag == None:
                return None
            else:
                return child_tag.text.strip().encode('utf-8')

        self.all_results = self._read_all_pages()
        # TODO: handle cases where the title background is gray
        result_dict = {
            'name': self._get_tag_info('a', 'name-link',),
            'category': self._get_tag_info('a', 'category'),
            'type': self._get_tag_info('span', 'type-name'),
            'views': self._integer(_find('div', 'view-count-value')),
            'topics': None,
            'descrip': self._get_tag_info('div', 'description')
        }

        self.datasets = self.datasets.append(result_dict, ignore_index=True)

        return 

    @staticmethod
    def _integer(number_string):
        #print(number_string)
        return int(number_string.decode().replace(',',''))

    def make_csv(self, folder='output/'):

        file_name = re.sub(r"[\.\[\]\/(]", r"_", re.findall(r'.+(?=/browse)', self.name)[0])+'.csv'
        if self.datasets is not None:
            print('data is coming...')
            self.datasets.to_csv(folder + file_name, index=False)
            print('Exported file: ' + file_name)

        return


def visit_all_sites(file_path='data/local_open_data_portals.csv'):

    print('Scraping all Socrata sites. This may take a few minutes.\n')
    all_places_df = pd.read_csv(file_path)
    all_places = {}
    for row in all_places_df.iterrows():
        new_place = Place(row[1].to_dict())
        all_places[new_place.name] = new_place
    socrata_places = {k: v for k, v in all_places.items()
        if (v.datasets is not None) and not v.datasets.empty}

    return all_places, socrata_places

def make_csvs(dict_, folder='output/'):

    for place in dict_.values():
        place.make_csv(folder)

    return

if __name__ == '__main__':

    all_places, socrata_places = visit_all_sites()
    make_csvs(socrata_places)
