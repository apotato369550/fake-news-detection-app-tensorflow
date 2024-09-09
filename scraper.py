import newspaper
from newspaper import Article
from newspaper import Source
import pandas as pd
import nltk

# nltk.download("punkt_tab")

# Let's say we wanted to download articles from Gamespot (which is a web site that discusses video games)
try:
    gamespot = newspaper.build("https://www.bbc.com/news", memoize_articles = False) 
    print("Articles obtained")
except:
    print("An error occured")
# I set memoize_articles to False, because I don't want it to cache and save the articles to memory, run after run.
# Fresh run, everytime we run execute this script essentially

final_df = pd.DataFrame()

article_count = 0;

for each_article in gamespot.articles:
    print(f"Article Count: {article_count + 1}")
    if article_count >= 5:
        break  # Stop after 10 articles
    each_article.download()
    each_article.parse()
    each_article.nlp()

    temp_df = pd.DataFrame({
        'Title': [each_article.title if each_article.title else 'No Title'],
        'Authors': [each_article.authors if each_article.authors else 'Unknown Author'],
        'Text': [each_article.text if each_article.text else 'No Text Available'],
        'Summary': [each_article.summary if each_article.summary else 'No Summary Available'],
        'published_date': [each_article.publish_date if each_article.publish_date else 'Unknown Date'],
        'Source': [each_article.source_url if each_article.source_url else 'Unknown Source']
    })

    final_df = pd.concat([final_df, temp_df], ignore_index = True)
    article_count += 1
  
# From here you can export this Pandas DataFrame to a csv file
final_df.to_csv('my_scraped_articles.csv')