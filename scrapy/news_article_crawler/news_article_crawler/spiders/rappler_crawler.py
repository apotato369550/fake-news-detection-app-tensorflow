import csv
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from scrapy.exceptions import CloseSpider

class RapplerCrawler(CrawlSpider):
    name = "rappler_crawler"
    allowed_domains = ["rappler.com"]
    start_urls = ["https://www.rappler.com/"]

    # Limit for the number of unique links
    link_limit = 3
    crawled_links = set()  # Use a set to store unique URLs

    # Open CSV file to write headers
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file = open('rappler_content.csv', 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['title', 'text'])  # Write the CSV headers

    # Rule to follow all links on the site
    rules = (
        Rule(LinkExtractor(
            allow=(),
            deny_domains=["facebook.com", "twitter.com"],
            deny=[r'sharer', r'intent/tweet', r'utm_source=fb_share', r'utm_source=tw_share']  # Exclude specific patterns
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        current_url = response.url

        # Check if the URL belongs to a blocked domain
        if self.is_blocked_domain(current_url):
            print(f"Current url {current_url} is blocked")
            return  # Skip this URL if it's from a blocked domain

        # Check if the final subdirectory has fewer than 3 dashes
        if not self.has_enough_dashes(current_url):
            print(f"Current url {current_url} does not have enough dashes")
            return  # Skip the URL if it doesn't meet the dash criteria

        # Check if we've reached the limit of unique links
        if len(self.crawled_links) >= self.link_limit:
            raise CloseSpider(reason=f"Reached the limit of {self.link_limit} unique links.")

        # Extract the title (h1 tag) and page content (p tags)
        title = response.css('h1::text').get()
        paragraphs = response.css('p::text').getall()

        # Debugging: Print the extracted title and content
        print(f"Extracted title: {title}")
        print(f"Extracted paragraphs: {paragraphs}")

        # Combine all paragraphs into a single string
        page_content = ' '.join(paragraphs)

        # Debugging: Check if title and content exist
        if not title:
            print(f"No title found on {current_url}")
        if not page_content.strip():
            print(f"No content found on {current_url}")

        if title and page_content and current_url not in self.crawled_links:
            self.crawled_links.add(current_url)  # Add the URL to the set of unique links

            # Write title and content to the CSV file
            self.csv_writer.writerow([title, page_content])

            # Debugging: Confirmation that data is being written
            print(f"Data written to CSV for URL: {current_url}")

            yield {
                'url': current_url,
                'title': title,
                'content': page_content,
            }

        # Extract and process internal links found on this page
        yield from self.extract_internal_links(response)

    def extract_internal_links(self, response):
        # Use LinkExtractor to extract all links from the page
        link_extractor = LinkExtractor()
        links = link_extractor.extract_links(response)

        # Iterate through the links found within the article
        for link in links:
            internal_url = link.url

            # Check if the internal link belongs to a blocked domain
            if self.is_blocked_domain(internal_url):
                continue  # Skip this link if it's from a blocked domain

            # Check if the final subdirectory has fewer than 3 dashes
            if not self.has_enough_dashes(internal_url):
                continue  # Skip the URL if it doesn't meet the dash criteria

            # Add the internal URL to the crawl queue by yielding a new request
            if len(self.crawled_links) < self.link_limit:  # Only queue if limit is not reached
                yield Request(internal_url, callback=self.parse_item)
            else:
                raise CloseSpider(reason=f"Reached the limit of {self.link_limit} unique links.")

    def is_blocked_domain(self, url):
        """Custom method to check if the URL belongs to a blocked domain."""
        blocked_domains = ["twitter.com", "facebook.com", "youtube.com"]
        for domain in blocked_domains:
            if domain in url or "rappler.com" not in url:
                return True  # URL is from a blocked domain
        return False  # URL is not from a blocked domain
    
    def has_enough_dashes(self, url):
        """Check if the URL path (excluding domain) has at least 3 dashes."""
        # Extract the path portion of the URL (everything after the domain)
        path = url.split(self.allowed_domains[0])[-1]
        
        # Count the dashes in the entire path
        dash_count = path.count('-')
        
        # Return True if there are 3 or more dashes in the URL path
        return dash_count >= 3

    def closed(self, reason):
        """Close the CSV file when the spider finishes."""
        self.csv_file.close()
