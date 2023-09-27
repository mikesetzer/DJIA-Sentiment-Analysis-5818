from django.db import models


class Portfolio(models.Model):
    """A group of stocks held in a portfolio"""
    name = models.CharField(max_length=20, help_text="Abbreviated name of the portfolio.")
    description = models.CharField(max_length=100, help_text="Description of the portfolio.")

    def __str__(self):
        return self.name + " - " + self.description


class Stock(models.Model):
    """A publicly traded stock"""
    ticker = models.CharField(max_length=10, help_text="The ticker associated with the stock.")
    company = models.CharField(max_length=10, help_text="The name of the company that issued the stock.")
    portfolio = models.ForeignKey(Portfolio,
                                  on_delete=models.CASCADE)  # For purposes of our project, a Stock can only belong to one Portfolio

    def __str__(self):
        return self.ticker + " - " + self.company


class StockPrice(models.Model):
    """The closing stock price on a given date"""

    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for the stock price.")
    price = models.DecimalField(help_text="The closing stock price.", max_digits=18, decimal_places=4)

    def __str__(self):
        return self.ticker.ticker + " - " + self.date + " - " + self.price


class Sentiment(models.Model):
    """Represents the sentiment score for a given stock on a given date"""

    class SentimentRecommendation(models.TextChoices):
        BUY = "BUY", "Buy"
        HOLD = "HOLD", "Hold"
        SELL = "SELL", "Sell"

    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for which the sentiment score was calculated.")
    score = models.DecimalField(help_text="The sentiment score.", max_digits=18, decimal_places=16)
    recommendation = models.CharField(help_text="The action recommended for the stock.",
                                      choices=SentimentRecommendation.choices, max_length=20)

    def __str__(self):
        return self.ticker.ticker + " - " + self.date + " - " + self.score


class SentimentDetail(models.Model):
    """Represents the individual sentiments captured for a given stock on a given date"""

    class SentimentChoices(models.IntegerChoices):
        NEGATIVE = -1
        NEUTRAL = 0
        POSITIVE = 1

    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date for which the sentiment score was calculated.")
    sentiment = models.IntegerField(choices=SentimentChoices.choices)

    def __str__(self):
        return self.ticker.ticker + " - " + self.date + " - " + self.sentiment
