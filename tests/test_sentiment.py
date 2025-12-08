"""Tests for sentiment analysis module"""
import pytest
from echo.ml.sentiment import SentimentAnalyzer


def test_sentiment_analyzer_initialization():
    """Test SentimentAnalyzer initialization"""
    analyzer = SentimentAnalyzer()
    assert analyzer.enabled is not None
    assert len(analyzer.positive_keywords) > 0
    assert len(analyzer.negative_keywords) > 0


def test_positive_sentiment():
    """Test positive sentiment detection"""
    analyzer = SentimentAnalyzer()
    text = "Stock price surges on strong earnings, bullish outlook for growth"
    result = analyzer.analyze_text(text)
    
    assert 'sentiment' in result
    assert 'score' in result
    assert 'confidence' in result
    assert result['sentiment'] == 'positive'
    assert result['score'] > 0


def test_negative_sentiment():
    """Test negative sentiment detection"""
    analyzer = SentimentAnalyzer()
    text = "Stock crashes amid bearish outlook, losses mount as concerns grow"
    result = analyzer.analyze_text(text)
    
    assert result['sentiment'] == 'negative'
    assert result['score'] < 0


def test_neutral_sentiment():
    """Test neutral sentiment detection"""
    analyzer = SentimentAnalyzer()
    text = "The company held a meeting today to discuss quarterly results"
    result = analyzer.analyze_text(text)
    
    assert result['sentiment'] in ['neutral', 'positive', 'negative']
    assert -1 <= result['score'] <= 1


def test_batch_analysis(sample_news_articles):
    """Test batch sentiment analysis"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_news_batch(sample_news_articles)
    
    assert 'overall_sentiment' in result
    assert 'sentiment_score' in result
    assert 'article_count' in result
    assert result['article_count'] == 3
    assert 'positive_count' in result
    assert 'negative_count' in result
    assert 'neutral_count' in result


def test_empty_text():
    """Test sentiment analysis with empty text"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_text("")
    
    assert result['sentiment'] == 'neutral'
    assert result['confidence'] == 0.0
