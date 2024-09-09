import pandas as pd
from sklearn.utils import shuffle
import requests
from bs4 import BeautifulSoup
import csv

def gatherFromTrueAndFalse(df):
    true_path = 'True.csv'
    fake_path = 'Fake.csv'

    # Load the true and fake news data from CSV files
    true_df = pd.read_csv(true_path)
    fake_df = pd.read_csv(fake_path)

    # Add Labels
    true_df['true'] = 1
    fake_df['true'] = 0

    # Select the relevant columns and concatenate them to the passed DataFrame
    df = pd.concat([df, true_df[['title', 'text', 'true']], fake_df[['title', 'text', 'true']]])

    # Return the updated DataFrame
    return df


def scrape_articles_from_url(url):
    """Scrapes titles and texts from articles on a given news website."""
    articles = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example of extracting titles and text for a generic news website
        # Modify this part according to the website's structure
        for article in soup.find_all('article'):
            title_tag = article.find('h1') or article.find('h2') or article.find('h3')
            text_tag = article.find('p')

            if title_tag and text_tag:
                title = title_tag.get_text(strip=True)
                text = ' '.join([p.get_text(strip=True) for p in article.find_all('p')])
                articles.append({'title': title, 'text': text, 'true': 1})

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
    
    return articles

def scrapeTheWebTrue(df):
    """
    changes i want.
    initial url, then scrape different article urls on the website. visit them, then scrape the content from there
    """

    urls = [
        "https://www.bbc.com", 
        "https://www.aljazeera.com", 
        "https://www.forbes.com"
        # Add more news website URLs as needed
    ]
    
    all_articles = []
    
    for url in urls:
        print(f"Scraping articles from {url}")
        articles = scrape_articles_from_url(url)
        all_articles.extend(articles)
    
    # Save to CSV
    with open('scraped_articles.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'text', 'true'])
        writer.writeheader()
        for article in all_articles:
            writer.writerow(article)

    print(f"Scraped {len(all_articles)} articles and saved to 'scraped_articles.csv'.")
    return df

def generateTrainData():
    # Start with an empty DataFrame
    df = pd.DataFrame(columns=['title', 'text', 'true'])

    # Pass the DataFrame through the gatherFromTrueAndFalse function
    df = gatherFromTrueAndFalse(df)

    # Pass the DataFrame through the scrapeTheWeb function
    # df = scrapeTheWebTrue(df)

    # Shuffle the DataFrame
    df = shuffle(df).reset_index(drop=True)

    # Save the DataFrame to a CSV file
    df.to_csv('combined_data.csv', index=False)

# Call the generateTrainData function
# generateTrainData()
scrapeTheWebTrue("")