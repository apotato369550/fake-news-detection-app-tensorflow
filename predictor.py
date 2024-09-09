import joblib
import numpy as np
from keras import models
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# Example lists of trusted and untrusted sources

trusted_sources = [
    "bbc.com", "nytimes.com", "theguardian.com", "washingtonpost.com", 
    "reuters.com", "apnews.com", "npr.org", "bloomberg.com", 
    "aljazeera.com", "forbes.com", "wsj.com", "economist.com", 
    "ft.com", "cnbc.com", "theatlantic.com", "politico.com", 
    "time.com", "nature.com", "sciencemag.org", "pbs.org", 
    "nationalgeographic.com", "huffpost.com", "abcnews.go.com", 
    "cbsnews.com", "nbcnews.com", "usatoday.com", "latimes.com", 
    "chicagotribune.com", "boston.com", "bostonglobe.com", 
    "axios.com", "newsweek.com", "usatoday.com", "vox.com", 
    "wired.com", "techcrunch.com", "slate.com", "thehill.com", 
    "democracynow.org", "msnbc.com", "seattletimes.com", "miamiherald.com", 
    "denverpost.com", "startribune.com", "rappler.com", "inquirer.net", 
    "philstar.com", "gmanetwork.com", "abs-cbn.com", "cnnphilippines.com", 
    "scmp.com", "straitstimes.com", "japantimes.co.jp", "channelnewsasia.com", 
    "sydney.edu.au", "smh.com.au", "theage.com.au", "afr.com", 
    "dw.com", "lemonde.fr", "spiegel.de", "zeit.de", 
    "elpais.com", "elmundo.es", "corriere.it", "repubblica.it", 
    "lefigaro.fr", "liberation.fr", "france24.com", "rfi.fr", 
    "rte.ie", "irishtimes.com", "thejournal.ie", "independent.co.uk", 
    "telegraph.co.uk", "ft.com", "economictimes.indiatimes.com", 
    "livemint.com", "thehindu.com", "indiatoday.in", "ndtv.com", 
    "abc.net.au", "news.com.au", "nzherald.co.nz", "thetimes.co.uk", 
    "dailymail.co.uk", "independent.co.uk", "metro.co.uk", 
    "irishexaminer.com", "almasryalyoum.com", "asharq.com", 
    "alwasatnews.com", "gulfnews.com", "thenational.ae", "aawsat.com", 
    "koreaherald.com", "joongang.co.kr", "koreatimes.co.kr", 
    "chinadaily.com.cn", "globaltimes.cn", "xinhuanet.com", 
    "peoplesdaily.com.cn"
]
untrusted_sources = [
    "fakenews.com", "clickbait.com", "unreliable.com", "infowars.com", 
    "theonion.com", "breitbart.com", "naturalnews.com", "beforeitsnews.com", 
    "newspunch.com", "prntly.com", "yournewswire.com", "rt.com", 
    "sputniknews.com", "dailystormer.su", "thegatewaypundit.com", 
    "conservativebyte.com", "worldtruth.tv", "activistpost.com", 
    "whatdoesitmean.com", "truthuncensored.net", "therealstrategy.com", 
    "nodisinfo.com", "nowtheendbegins.com", "truthuncensored.net", 
    "dcclothesline.com", "truepundit.com", "wnd.com", "veteranstoday.com", 
    "theblaze.com", "westernjournal.com", "realfarmacy.com", 
    "libertyonenews.com", "theduran.com", "newswars.com", 
    "sott.net", "freedomoutpost.com", "21stcenturywire.com", 
    "zerohedge.com", "naturalnewsblogs.com", "prisonplanet.com", 
    "godlikeproductions.com", "abovetopsecret.com", "collective-evolution.com", 
    "beforeitsnews.com", "americanthinker.com", "bitchute.com", 
    "trunews.com", "dailycaller.com", "dailywire.com", "gellerreport.com", 
    "jihadwatch.org", "creepingsharia.com", "frontpagemag.com", 
    "humanevents.com", "infostormer.com", "johngaltfla.com", 
    "libertyheadlines.com", "moonbattery.com", "newstarget.com", 
    "offguardian.org", "projectveritas.com", "redstate.com", 
    "rightwingnews.com", "shadowproof.com", "sovereignman.com", 
    "statenation.co", "thefederalist.com", "thegatewaypundit.com", 
    "thepoliticalinsider.com", "truththeory.com", "usdefensewatch.com", 
    "usanewshome.com", "usherald.com", "veteranstoday.com", 
    "wearechange.org", "yellowhammernews.com", "zenithnews.com", 
    "zootfeed.com", "conservativefighters.org", "conservativemedia.com", 
    "truthbroadcastnetwork.com", "americandigitalnews.com", 
    "americannewsx.com", "americanpatriotdaily.com", 
    "bigleaguepolitics.com", "bluntforcetruth.com", "bovnews.com", 
    "bullshido.net", "buzzpo.com", "callthecops.net", "calvinsworldnews.com", 
    "conservativeinfidel.com", "conservativeoutfitters.com", 
    "conservativereview.com", "dailybuzzlive.com", "dailyheadlines.net", 
    "eutimes.net", "fprnradio.com", "govtslaves.info", "gulagbound.com", 
    "huzlers.com", "investmentwatchblog.com"
]

# Load the saved model
model = models.load_model('fake_news_model.h5')

# Load the saved vectorizers
vectorizer_title = joblib.load('vectorizer_title.pkl')
vectorizer_text = joblib.load('vectorizer_text.pkl')

def predict_fake_news(title, text):
    # Preprocess the input title and text using the loaded vectorizers
    title_features = vectorizer_title.transform([title]).toarray()
    text_features = vectorizer_text.transform([text]).toarray()
    
    # Predict using the loaded model
    prediction = model.predict([title_features, text_features])[0][0]
    
    # Calculate percentage probability
    real_probability = prediction * 100  # Probability that the article is real
    fake_probability = (1 - prediction) * 100  # Probability that the article is fake
    
    return f"This article is {real_probability:.2f}% Real and {fake_probability:.2f}% Fake"

# Example usage of the predict function

def extract_title_and_text(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title
        title = soup.title.string if soup.title else "No title found"

        # Extract the main article text (basic approach)
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])

        return title, text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None, None

def get_domain_from_url(url):
    """Extract the domain name from a URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain.replace("www.", "")  # Remove 'www.' if present

def is_trusted_source(domain):
    """Check if the domain is in the trusted or untrusted lists."""
    if domain in trusted_sources:
        return "trusted"
    elif domain in untrusted_sources:
        return "untrusted"
    else:
        return "unknown"

def predict_fake_news_from_url(url):
    # Step 1: Extract the domain
    domain = get_domain_from_url(url)
    
    # Step 2: Check if the domain is trusted, untrusted, or unknown
    source_status = is_trusted_source(domain)
    
    if source_status == "trusted":
        print("This is a trusted news source. Less likely to be fake.")
    elif source_status == "untrusted":
        print("This is an untrusted news source. More likely to be fake.")
    
    # Step 3: Proceed to predict if the source is unknown
    title, text = extract_title_and_text(url)
    if title and text:
        return predict_fake_news(title, text)
    else:
        return "Could not extract title or text from the URL."


# Example usage:
url = "https://www.rappler.com/philippines/mindanao/exhausted-cops-weary-apollo-quiboloy-group-standoff-davao-manhunt/"
prediction = predict_fake_news_from_url(url)
print(prediction)