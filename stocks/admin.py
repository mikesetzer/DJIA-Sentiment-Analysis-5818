from django.contrib import admin

from stocks.models import (Stock, Portfolio, StockPrice, SentimentScore, Sentiment)

# Register your models here.
admin.site.register(Stock)
admin.site.register(Portfolio)
admin.site.register(StockPrice)
admin.site.register(SentimentScore)
admin.site.register(Sentiment)
