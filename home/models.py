from django.db import models


class Stock(models.Model):
    """A publicly traded stock"""
    ticker = models.CharField(max_length=10, help_text="The ticker associated with the stock.")
    company = models.CharField(max_length=10, help_text="The name of the company that issued the stock.")

    def __str__(self):
        return '{} - {}'.format(self.ticker, self.company)


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
        return '{} - {} - {} - {}'.format(self.stock.ticker, self.date, self.sentiment_score, self.total_recommendation)


class StockQuote(models.Model):
    """The stock quote data from the finnhub api on a given date.
    Refer to https://finnhub.io/docs/api/quote."""

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for the stock quote.")
    current_price = models.DecimalField(help_text="The current stock price. ('c')", max_digits=18, decimal_places=4)
    change = models.DecimalField(help_text="The change in stock price. ('d')", max_digits=18, decimal_places=4)
    percent_change = models.DecimalField(help_text="The percent change in stock price. ('dp')", max_digits=18, decimal_places=4)
    high_price = models.DecimalField(help_text="The high price of the day. ('h')", max_digits=18, decimal_places=4)
    low_price = models.DecimalField(help_text="The low price of the day. ('l')", max_digits=18, decimal_places=4)
    open_price = models.DecimalField(help_text="The open price of the day. ('o')", max_digits=18, decimal_places=4)
    prev_close_price = models.DecimalField(help_text="The previous closing price. ('pc')", max_digits=18, decimal_places=4)
    time_stamp = models.IntegerField(help_text="The timestamp when the quote was retrieved. ('t')")


    def __str__(self):
        return '{} - {} - {}'.format(self.stock.ticker, self.date, self.current_price)
