from django.db import models


class Stock(models.Model):
    """A publicly traded stock"""
    ticker = models.CharField(max_length=10, help_text="The ticker associated with the stock.")
    company = models.CharField(max_length=10, help_text="The name of the company that issued the stock.")

    def __str__(self):
        return self.ticker + " - " + self.company


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
    sentiment_score = models.CharField(help_text="The sentiment score.", choices=SentimentScoreChoices.choices,
                                       max_length=20)
    stock_recommendation = models.CharField(help_text="The action recommended for the stock.",
                                            choices=RecommendationChoices.choices, max_length=20)
    total_recommendation = models.CharField(help_text="The final action recommended for the stock.",
                                            choices=RecommendationChoices.choices, max_length=20)

    def __str__(self):
        return self.stock.ticker + " - " + str(self.date) + " - " + str(self.sentiment_score) + " - " + str(
            self.total_recommendation)
