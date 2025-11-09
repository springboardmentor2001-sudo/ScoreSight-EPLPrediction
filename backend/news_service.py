import requests
import feedparser
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class EPLNewsService:
    def __init__(self):
        self.newsapi_key = "4ff61e81a6c646208b34d3b5c42817b2"
        self.rss_feeds = [
            'https://feeds.bbci.co.uk/sport/football/premier-league/rss.xml',
            'https://www.skysports.com/rss/12040',
            'https://www.theguardian.com/football/premierleague/rss'
        ]
    
    def fetch_rss_news(self) -> List[Dict]:
        """Fetch news from RSS feeds (primary method)"""
        all_articles = []
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Get latest 10 from each feed
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary if hasattr(entry, 'summary') else entry.description,
                        'published': entry.published if hasattr(entry, 'published') else entry.updated,
                        'source': feed.feed.title if hasattr(feed.feed, 'title') else feed_url,
                        'type': 'rss'
                    }
                    all_articles.append(article)
            except Exception as e:
                print(f"Error fetching RSS feed {feed_url}: {e}")
                continue
        
        return all_articles
    
    def fetch_newsapi_news(self) -> List[Dict]:
        """Fetch news from NewsAPI (backup method)"""
        try:
            # Calculate date from 1 week ago for freshness
            one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': 'premier league OR "english premier league" OR EPL',
                'from': one_week_ago,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20,
                'apiKey': self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', []):
                    articles.append({
                        'title': article['title'],
                        'link': article['url'],
                        'summary': article['description'] or '',
                        'published': article['publishedAt'],
                        'source': article['source']['name'],
                        'type': 'newsapi'
                    })
                
                return articles
            else:
                print(f"NewsAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching NewsAPI: {e}")
            return []
    
    def get_all_news(self, limit: int = 20) -> List[Dict]:
        """Get all news combining both sources"""
        try:
            # Primary: RSS feeds
            rss_articles = self.fetch_rss_news()
            
            # Backup: NewsAPI if RSS fails or gives limited results
            if len(rss_articles) < 5:
                newsapi_articles = self.fetch_newsapi_news()
                all_articles = rss_articles + newsapi_articles
            else:
                all_articles = rss_articles
            
            # Remove duplicates based on title similarity
            unique_articles = self._remove_duplicates(all_articles)
            
            # Sort by date (newest first)
            unique_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
            
            return unique_articles[:limit]
            
        except Exception as e:
            print(f"Error in get_all_news: {e}")
            # Fallback to NewsAPI only
            return self.fetch_newsapi_news()[:limit]
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Create a simplified title for comparison
            simple_title = article['title'].lower().replace('premier league', '').strip()[:50]
            
            if simple_title not in seen_titles:
                seen_titles.add(simple_title)
                unique_articles.append(article)
        
        return unique_articles

# Create global instance
news_service = EPLNewsService()