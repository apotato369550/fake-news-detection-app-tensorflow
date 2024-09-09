import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from tqdm import tqdm
import urllib3
import warnings

# Suppress only the specific InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_article_urls(news_website_url, max_urls=150):
    # Initialize a queue for URLs to crawl
    queue = deque([news_website_url])
    
    # Set to store unique article URLs
    article_urls = set()

    # Blacklist of domains to ignore
    blacklist = ['facebook.com', 'twitter.com', 'youtube.com', 'x.com', 'instagram.com']

    # Extract the domain of the news website
    website_domain = urlparse(news_website_url).netloc

    # Progress bar initialization
    pbar = tqdm(total=max_urls, desc=f'Crawling {news_website_url}', unit='url')

    # Keep crawling until we have enough URLs or the queue is empty
    while queue and len(article_urls) < max_urls:
        # Get the next URL from the queue
        current_url = queue.popleft()
        
        # Update progress bar text to show the current URL being crawled
        pbar.set_postfix_str(f'Current URL: {current_url[:50]}...')

        try:
            # Send a request to the current URL with SSL verification disabled
            response = requests.get(current_url, verify=False)
            
            # Check if the request was successful
            if response.status_code != 200:
                continue
            
            # Parse the website content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags
            a_tags = soup.find_all('a')

            # Loop through all the <a> tags
            for tag in a_tags:
                href = tag.get('href')
                if href and 'http' not in href:  # Handle relative URLs
                    href = urljoin(news_website_url, href)
                
                # Extract the domain of the URL to check against the blacklist
                domain = urlparse(href).netloc

                # Ensure the URL contains the website's domain, is not blacklisted, and isn't already visited
                if href and website_domain in href and not any(black_domain in domain for black_domain in blacklist):
                    # Extract the path and check the final subdirectory
                    path = urlparse(href).path
                    final_subdirectory = path.rstrip('/').split('/')[-1]

                    # Count the number of hyphens in the final subdirectory
                    hyphen_count = final_subdirectory.count('-')

                    # If the final subdirectory has more than 3 hyphens, save it as an article URL
                    if hyphen_count > 3:
                        if href not in article_urls:
                            article_urls.add(href)
                            pbar.update(1)
                    else:
                        # If the final subdirectory has 3 or fewer hyphens, crawl through but don't save
                        queue.append(href)
                    
                    # Stop adding URLs if we reach the desired count
                    if len(article_urls) >= max_urls:
                        break

        except requests.RequestException as e:
            print(f"Failed to retrieve {current_url}: {e}")

    # Close the progress bar
    pbar.close()
    
    return list(article_urls)

def save_urls_to_file(urls, filename):
    # Read existing URLs from the file if it exists
    try:
        with open(filename, 'r') as file:
            existing_urls = set(file.read().splitlines())
    except FileNotFoundError:
        existing_urls = set()

    # Combine new URLs with existing ones and remove duplicates
    all_urls = existing_urls.union(set(urls))

    # Save the combined URLs back to the file
    with open(filename, 'w') as file:
        for url in all_urls:
            file.write(url + '\n')

# Example usage
news_websites = [
    'https://news.abs-cbn.com',
]

all_article_urls = []
for website in news_websites:
    article_urls = get_article_urls(website, max_urls=150)
    all_article_urls.extend(article_urls)

# Store the URLs in a file named 'article_urls.txt'
save_urls_to_file(all_article_urls, 'article_urls.txt')

print(f"Found {len(all_article_urls)} article URLs and saved them to 'article_urls.txt'.")
