"""
Sentiment analysis module for financial news and social media
Uses NLP techniques to analyze market sentiment
"""
from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re
from ..utils.logging import get_logger
from ..utils.config import config

log = get_logger("SentimentAnalyzer")


class SentimentAnalyzer:
    """
    Analyze sentiment from financial news and text
    Placeholder for FinBERT or similar models
    """
    
    def __init__(self):
        self.model_path = config.finbert_model_path
        self.enabled = config.enable_sentiment_analysis
        self.model = None
        
        # Simple keyword-based sentiment (fallback)
        self.positive_keywords = {
            'bullish', 'growth', 'profit', 'gain', 'rise', 'surge', 'rally',
            'positive', 'strong', 'beat', 'exceed', 'outperform', 'upside',
            'momentum', 'upgrade', 'buy', 'long', 'optimistic', 'boost'
        }
        
        self.negative_keywords = {
            'bearish', 'loss', 'decline', 'fall', 'drop', 'crash', 'plunge',
            'negative', 'weak', 'miss', 'underperform', 'downside', 'risk',
            'downgrade', 'sell', 'short', 'pessimistic', 'concern', 'threat'
        }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text snippet
        
        Returns:
            Dictionary with sentiment, score, and confidence
        """
        if not self.enabled or not text:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'disabled'
            }
        
        try:
            # Try to use FinBERT model if available
            if self.model:
                return self._finbert_analysis(text)
            else:
                return self._keyword_analysis(text)
        except Exception as e:
            log.exception(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _keyword_analysis(self, text: str) -> Dict:
        """Simple keyword-based sentiment analysis"""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        positive_count = len(words & self.positive_keywords)
        negative_count = len(words & self.negative_keywords)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.3,
                'method': 'keyword',
                'positive_words': 0,
                'negative_words': 0
            }
        
        # Calculate sentiment score (-1 to 1)
        score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine sentiment label
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Confidence based on number of sentiment words found
        confidence = min(0.8, 0.3 + (total_sentiment_words / 10))
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': round(confidence, 2),
            'method': 'keyword',
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def _finbert_analysis(self, text: str) -> Dict:
        """
        FinBERT-based sentiment analysis (placeholder)
        Would require transformers library and model loading
        """
        log.info("FinBERT analysis not yet implemented, using keyword analysis")
        return self._keyword_analysis(text)
    
    def analyze_news_batch(self, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment across multiple news articles
        
        Args:
            articles: List of dictionaries with 'title', 'description', 'source', 'publishedAt'
            
        Returns:
            Aggregate sentiment analysis
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = []
        scores = []
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            result = self.analyze_text(text)
            sentiments.append(result['sentiment'])
            scores.append(result['score'])
        
        # Calculate aggregate metrics
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        neutral_count = sentiments.count('neutral')
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine overall sentiment
        if positive_count > negative_count * 1.5:
            overall = 'positive'
        elif negative_count > positive_count * 1.5:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        confidence = min(0.9, 0.4 + (len(articles) / 20))
        
        return {
            'overall_sentiment': overall,
            'sentiment_score': round(avg_score, 3),
            'confidence': round(confidence, 2),
            'article_count': len(articles),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_distribution': {
                'positive': round(positive_count / len(articles) * 100, 1),
                'negative': round(negative_count / len(articles) * 100, 1),
                'neutral': round(neutral_count / len(articles) * 100, 1)
            }
        }


class NewsProvider:
    """Fetch financial news for sentiment analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.news_api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """
        Fetch news articles (placeholder implementation)
        Would require actual API integration
        """
        if not self.api_key:
            log.warning("News API key not configured")
            return []
        
        try:
            import requests
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'apiKey': self.api_key,
                'language': 'en'
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            log.exception(f"Error fetching news: {e}")
            return []
    
    def get_ticker_sentiment(self, ticker: str, company_name: Optional[str] = None) -> Dict:
        """Get sentiment analysis for a specific stock ticker"""
        query = f"{ticker} stock"
        if company_name:
            query += f" OR {company_name}"
        
        articles = self.get_news(query, days_back=7)
        
        analyzer = SentimentAnalyzer()
        sentiment_result = analyzer.analyze_news_batch(articles)
        sentiment_result['ticker'] = ticker
        sentiment_result['query'] = query
        
        return sentiment_result


def get_market_sentiment(tickers: List[str]) -> Dict[str, Dict]:
    """
    Get sentiment analysis for multiple tickers
    
    Returns:
        Dictionary mapping ticker to sentiment analysis
    """
    results = {}
    news_provider = NewsProvider()
    
    for ticker in tickers:
        try:
            sentiment = news_provider.get_ticker_sentiment(ticker)
            results[ticker] = sentiment
        except Exception as e:
            log.exception(f"Error getting sentiment for {ticker}: {e}")
            results[ticker] = {
                'overall_sentiment': 'neutral',
                'confidence': 0.0,
                'error': str(e)
            }
    
    return results
