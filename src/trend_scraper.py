from pytrends.request import TrendReq
from pytrends import exceptions
import time

def get_trending_topics():
    try:
        pytrends = TrendReq(hl='en-IN', tz=330)
        pytrends.build_payload(kw_list=["AI tools", "tech", "earn money online"])
        data = pytrends.related_queries()
        time.sleep(5) # Add a delay to avoid rate limiting
        queries = []
        for topic in data.values():
            if topic['top'] is not None:
                queries += [q['query'] for q in topic['top'].to_dict('records')]
        return queries
    except exceptions.TooManyRequestsError:
        print("Rate limit hit for Google Trends. Using fallback keywords.")
        return ["AI Automation", "Data Science Trends", "Machine Learning Applications", "n8n Workflows", "Future of AI"]
