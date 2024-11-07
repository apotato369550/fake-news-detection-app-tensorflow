from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from scrapy.exceptions import CloseSpider

class CrawlingSpider(CrawlSpider):
    name = "abs-cbn_crawler"
    allowed_domains = ["news.abs-cbn.com", "abs-cbn.com"]  # Add the allowed domain(s)
    start_urls = ["https://news.abs-cbn.com/", "https://abs-cbn.com/newsroom"]

    # Limit for the number of unique links
    link_limit = 100
    crawled_links = set()  # Use a set to store unique URLs

    # Rule to follow all links on the site
    rules = (
        Rule(LinkExtractor(
            allow=(), 
            deny_domains=[
                "facebook.com", 
                "twitter.com"
            ],deny=[r'sharer', r'intent/tweet', r'utm_source=fb_share', r'utm_source=tw_share']  # Exclude specific patterns
        ), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        current_url = response.url

        # Check if the URL belongs to a blocked domain
        if self.is_blocked_domain(current_url):
            return  # Skip this URL if it's from a blocked domain

        # Check if we've reached the limit of unique links
        if len(self.crawled_links) >= self.link_limit:
            raise CloseSpider(reason=f"Reached the limit of {self.link_limit} unique links.")

        # Extract the URL path and check if it has more than three dashes
        path = current_url.split('/')[-1]
        dash_count = path.count('-')

        # If the final subdirectory has more than three dashes and the URL is unique, process it
        if dash_count > 3 and current_url not in self.crawled_links:
            self.crawled_links.add(current_url)  # Add the URL to the set of unique links
            with open('abs-cbn_links.txt', 'a') as f:
                f.write(current_url + "\n")
            
            yield {
                'url': current_url,
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

            path = internal_url.split('/')[-1]
            dash_count = path.count('-')

            # If the final subdirectory has more than three dashes, process the internal URL
            if dash_count > 3 and internal_url not in self.crawled_links:
                self.crawled_links.add(internal_url)  # Add the URL to the set of unique links

                # Save the internal URL
                with open('abs-cbn_links.txt', 'a') as f:
                    f.write(internal_url + "\n")

                yield {
                    'internal_url': internal_url,
                }

            # Add the internal URL to the crawl queue by yielding a new request
            if len(self.crawled_links) < self.link_limit:  # Only queue if limit is not reached
                yield Request(internal_url, callback=self.parse_item)
            else:
                raise CloseSpider(reason=f"Reached the limit of {self.link_limit} unique links.")

    def is_blocked_domain(self, url):
        """Custom method to check if the URL belongs to a blocked domain."""
        blocked_domains = ["careers.abs-cbn.com", "ent.abs-cbn.com", "abs-cbn.com/download", "abs-cbn.com/newsroom/videos", "ddec1-0-en-ctp.trendmicro.com", "facebook.com", "twitter.com", "youtube.com"]
        for domain in blocked_domains:
            if domain in url or "abs-cbn.com" not in url:
                return True  # URL is from a blocked domain
        return False  # URL is not from a blocked domain
