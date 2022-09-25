'''
Outline: 
Link: https://github.com/topics
List of topics. Each topic - topic title, topic page URL and topic description
25 repositories for each topic
For each repository, repo name, username, stars and repo URL
CSV file in the following format:
Repo name,Username,Stars,Repo URL
three.js,mrdoob,69700,https://github.com/mrdoob/three.js
libgdx,libgdx,18300,https://github.com/libgdx/libgdx
''' 

from pickle import NONE
import requests 
topics_url = 'https://github.com/topics'
response = requests.get(topics_url)

page_contents = response.text
page_contents[:1000]

with open("webpage.html", "w", encoding="utf-8") as f:
    f.write(page_contents)

from bs4 import BeautifulSoup
doc = BeautifulSoup(page_contents, 'html.parser')
selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
topic_title_tags = doc.find_all('p', class_=selection_class)


desc_selector = 'f5 color-fg-muted mb-0 mt-1'
topic_desc_tags = doc.find_all('p', {'class': desc_selector})

topic_title_tag0 = topic_title_tags[0]
div_tag = topic_title_tag0.parent
topic_link_tags = doc.find_all('a', {"class": 'no-underline flex-grow-0'})

topic0_url = "https://github.com" + topic_link_tags[0]['href']

topic_titles = []
topic_descriptions = []
topic_urls = []
base_url = 'https://github.com'

for tag in topic_title_tags:
    topic_titles.append(tag.text)

for tag in topic_desc_tags:
    topic_descriptions.append(tag.text.strip())


for tag in topic_link_tags:
    topic_urls.append(base_url + tag['href'])


topics_dict = {
    'title': topic_titles,
    'description': topic_descriptions,
    'urls': topic_urls
}

import pandas as pd
topics_df = pd.DataFrame(topics_dict)

#print(topics_df)

print(topics_df.to_csv('topics.csv'))

#Getting information out of topic page

topic_page_url = topic_urls[0]

response = requests.get(topic_page_url)
#response.status_code

topic_doc = BeautifulSoup(response.text, 'html.parser')
h3_selection_class = "f3 color-fg-muted text-normal lh-condensed"
repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class } )
a_tags = repo_tags[0].find_all('a')

repo_url = base_url + a_tags[1]['href']
star_tags = topic_doc.find_all('span', {'class': 'Counter js-social-count'})
#print(star_tags[0].text.strip())

def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]) * 1000)
    return int(stars_str)

#FINAL CODE
import os

def get_topic_page(topic_urls):
     # Download the page
    response = requests.get(topic_urls)
    # Check successful response
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_urls))
        # Parse using Beautifulsoup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc
#print(get_repo_info(repo_tags[0], star_tags[0]))

def get_repo_info(h3_tag, star_tags):
    #returns all the requie+red info about a repository
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tags.text.strip())
    return username, repo_name, stars, repo_url


def get_topic_repos (topic_doc):
    # Get the h3 tags containing repo title, repo URL and username
    h3_selection_class = "f3 color-fg-muted text-normal lh-condensed"
    repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class})
    # Get star tags
    star_tags = topic_doc.find_all('span', {'class': 'Counter js-social-count'})

    topic_repos_dict = {
        'username': [],
        'repo_name': [],
        'stars': [],
        'repo_url': []
    }

    # Get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])

    return pd.DataFrame(topic_repos_dict)

#df = pd.DataFrame(get_topic_repos(get_topic_page(topic_urls[5])))
#print(df.to_csv('ansible.csv', index=None))

def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("The file {} already exists. Skipping....".format(path))
        return 
    topic_df = get_topic_repos(get_topic_page(topic_url))
    topic_df.to_csv(path, index=None) #we don't want to show rows numbers (None)

'''
Write a single function to:
1. Get the list of topics from the topics page
2. Get the list of top repos from the individual topic pages
3. Create CSV of the top repos from the topic
'''

def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.find_all('p', class_=selection_class) 
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)
    return topic_titles

def get_topic_descs(doc):
    desc_selector = 'f5 color-fg-muted mb-0 mt-1'
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_descriptions = []
    for tag in topic_desc_tags:
        topic_descriptions.append(tag.text.strip())
    return topic_descriptions

def get_topic_urls(doc):
    topic_link_tags = doc.find_all('a', {"class": 'no-underline flex-grow-0'})
    topic_urls = []
    base_url = 'https://github.com'

    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls



def scrape_topics():
    topics_url = 'https://github.com/topics'
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_urls))
    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'URL': get_topic_urls(doc)
    }
    return pd.DataFrame(topics_dict)


def scrape_topics_repos():
    print('Scraping list of topics')
    topics_df = scrape_topics()

    os.makedirs('data', exist_ok=True)

    for index, row in topics_df.iterrows():
        print('Scraping top repositories for "{}"'.format(row['title']))
        scrape_topic(row['URL'], 'data/{}.csv'.format(row['title']))

print(scrape_topics_repos())


