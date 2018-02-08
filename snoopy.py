import bs4, os, requests
import pandas as pd
import random
import time
import article

import logging
logger = logging.getLogger("Sojy ")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class SnopesParser(object):

    def __init__(self, start_url=None, max_page=2, **kwargs):
        self.start_url = start_url
        logger.info(" Wicked ways beneath the skin, let all who taste it now join in...")
        self.seed = 'http://www.snopes.com/category/facts/page/'
        self.max_page = max_page
        self.articles_dict = dict()

    def get_soup(self, url):
        '''
        Function to extract beautiful soup object from the html page.
        '''
        logger.info(" Getting data via requests")
        url_text = requests.get(url)
        url_text.raise_for_status()
        logger.info(" Souping data")
        soup = bs4.BeautifulSoup(url_text.text, 'html.parser')
        self.soup = soup
        return soup

    def article_parse(self, url):
        '''
        Function to loop over the soup and extract the articles as a dictionary of objects.
        '''
        soup = self.get_soup(url)
        articles_dict = dict()
        try:
            for i in soup.find_all('article'):
                #append article object to dictionary
                article = self.extract_article_info(i)
                articles_dict[article.post_num] = article
        except:
            pass
        #self.articles_dict = articles_dict
        return articles_dict


    def extract_article_info(self, article_content):

        '''
        Function to scrape the article features from the HTML.
        Iteratively taking the claim, date, truth statement, url, and post num
        '''

        art_object = article.snopes_article()
        art_object.title = article_content.find('h2').text
        art_object.date = article_content.find('p').find('span').text
        art_object.is_valid = article_content.find('span', {"itemprop": "alternateName"}).text
        art_object.url = article_content.find('a')['href']
        art_object.post_num = [i for i in article_content.find('a')['class'] if 'post-' in i][0]
        art_object.tags = [i for i in article_content.find('a')['class'] if 'tag-' in i]
        art_object.pub_date = article_content.find('meta', {"itemprop": "datePublished"})['content']
        art_object.mod_date = article_content.find('meta', {"itemprop": "dateModified"})['content']
        art_object.claim = article_content.find('meta', {"itemprop": "claimReviewed"})['content']

        return art_object

    def get_all_articles(self): #once finished running, this will end us with a dictionary of article classes as a class attribute.
        all_articles = dict()
        for i in range(1, self.max_page+1):
            #time.sleep(1) #sleep to not be a jerk
            url = self.seed + str(i)
            logger.info(" Getting articles from {}".format(url))
            articles_dict = self.article_parse(url)
            all_articles.update(articles_dict)
        self.all_articles = all_articles

    def format_articles(self):
        final_dict = dict()
        for i in self.all_articles:
            final_dict.update({i: self.all_articles[i].__dict__})
        self.data = pd.DataFrame.from_dict(final_dict, orient='index').reset_index(drop=True)

    def get_max_page(self):
        try:
            title = self.soup.find_all('div', class_='article-list-pagination')[0].find('span', class_='page-count').text
            max_page = [int(s) for s in title.split() if s.isdigit()]
            self.max_page = max(map(int, max_page))
        except:
            logger.info(" Unable to get max page")

    def run(self):
        self.get_all_articles()
        logger.info(" Formatting articles to a dataframe")
        self.format_articles()
        logger.info(" All set")

if __name__ == '__main__':

    x = SnopesParser(max_page=2)
    x.run()
    x.get_max_page()
    logger.info(" Final page size: {}".format(x.max_page))
    x.data.to_csv('test_snopes.csv', index=False, encoding='utf-8')
