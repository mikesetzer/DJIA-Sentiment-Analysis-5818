from datetime import date

from django.db import models


class Stock(models.Model):
    """A publicly traded stock"""
    ticker = models.CharField(max_length=10, help_text="The ticker associated with the stock.")
    company = models.CharField(max_length=10, help_text="The name of the company that issued the stock.")

    def __str__(self):
        return self.ticker + " - " + self.company


class Portfolio(models.Model):
    """A group of stocks held in a portfolio"""
    name = models.CharField(max_length=20, help_text="Abbreviated name of the portfolio.")
    description = models.CharField(max_length=100, help_text="Description of the portfolio.")
    stocks = models.ManyToManyField('Stock')

    def __str__(self):
        return self.name + " - " + self.description


class StockPrice(models.Model):
    """The closing stock price on a given date"""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date: date = models.DateField(help_text="Date for the stock price.")
    price = models.DecimalField(help_text="The closing stock price.", max_digits=18, decimal_places=4)

    def __str__(self):
        return self.stock.ticker + " - " + str(self.date) + " - " + str(self.price)


class Recommendation(models.Model):
    """Represents the recommendation for a given stock on a given date based on sentiment analysis"""

    class SentimentScoreChoices(models.TextChoices):
        NEGATIVE = "negative", "Negative"
        NEUTRAL = "neutral", "Neutral"
        POSITIVE = "positive", "Positive"

    class RecommendationChoices(models.TextChoices):
        STRONG_BUY = "Strong Buy", "Strong Buy"
        BUY = "Buy", "Buy"
        HOLD = "Hold", "Hold"
        SELL = "Sell", "Sell"
        STRONG_SELL = "Strong Sell", "Strong Sell"

    primary_key_text = models.CharField(max_length=50,
                                        help_text="Unique identifier made up of ticker symbol concatenated with the date ")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for which the recommendation was calculated.")
    sentiment_score = models.CharField(help_text="The sentiment score.",
                                       choices=SentimentScoreChoices.choices, max_length=20)
    stock_recommendation = models.CharField(help_text="The action recommended for the stock.",
                                            choices=RecommendationChoices.choices, max_length=20)
    total_recommendation = models.CharField(help_text="The final action recommended for the stock.",
                                            choices=RecommendationChoices.choices, max_length=20)

    def __str__(self):
        return self.stock.ticker + " - " + str(self.date) + " - " + str(self.sentiment_score) + " - " + str(self.total_recommendation)


class SentimentScore(models.Model):
    """Represents the sentiment score for a given stock on a given date"""

    class SentimentRecommendation(models.TextChoices):
        BUY = "BUY", "Buy"
        HOLD = "HOLD", "Hold"
        SELL = "SELL", "Sell"

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for which the sentiment score was calculated.")
    score = models.DecimalField(help_text="The sentiment score.", max_digits=18, decimal_places=16)
    recommendation = models.CharField(help_text="The action recommended for the stock.",
                                      choices=SentimentRecommendation.choices, max_length=20)

    def __str__(self):
        return self.stock.ticker + " - " + str(self.date) + " - " + str(self.score)


class Sentiment(models.Model):
    """Represents the individual sentiments captured for a given stock on a given date"""

    class SentimentChoices(models.IntegerChoices):
        NEGATIVE = -1
        NEUTRAL = 0
        POSITIVE = 1

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for which the sentiment score was calculated.")
    sentiment = models.IntegerField(choices=SentimentChoices.choices)

    def __str__(self):
        return self.stock.ticker + " - " + str(self.date) + " - " + str(self.sentiment)
