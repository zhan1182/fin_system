from mongoengine import * 


class PriceTarget(EmbeddedDocument):
    symbol = StringField(required=True)
    update_date = DateTimeField()
    target_average = FloatField()
    target_high = FloatField()
    target_low = FloatField()
    number_of_analysts = LongField()
    currency = StringField()


class KeyStats(EmbeddedDocument):
    query_date = DateTimeField(required=True)

    market_cap = LongField()
    pe_ratio = FloatField()
    beta = FloatField()

    ttm_eps = FloatField()
    ttm_dividend_rate = FloatField()
    dividend_yield = FloatField()
    next_dividend_date = StringField()
    ex_dividend_date = StringField()
    next_earnings_date = StringField()

    week_52_high = FloatField()
    week_52_low = FloatField()
    week_52_change = FloatField()
    
    avg_10_volume = LongField()
    avg_30_volume = LongField()

    day_200_movingavg = FloatField()
    day_50_movingavg = FloatField()

    max_change_percent = FloatField()
    year_5_change_percent = FloatField()
    year_2_change_percent = FloatField()
    year_1_change_percent = FloatField()
    ytd_change_percent = FloatField()
    month_6_change_percent = FloatField()
    month_3_change_percent = FloatField()
    month_1_change_percent = FloatField()
    day_30_change_percent = FloatField()
    day_5_change_percent = FloatField()


class BasicInfo(EmbeddedDocument):
    industry = StringField()
    sector = StringField()
    tags = ListField(StringField())
    state = StringField()


class DailyAdjusted(EmbeddedDocument):
    date = DateTimeField(required=True)

    open_price = FloatField()
    close_price = FloatField()
    high = FloatField()
    low = FloatField()
    volume = LongField()

    adjusted_close_price = FloatField()
    dividend = FloatField()
    split_coefficient = FloatField()
    

class StockDocument(Document):
    symbol = StringField(required=True)
    name = StringField(required=True)
    exchange = StringField(required=True)

    # Basic information
    basic_info = EmbeddedDocumentField(BasicInfo)

    # Technical indicators
    latest_key_stats = EmbeddedDocumentField(KeyStats)
    key_stats_ts = ListField(EmbeddedDocumentField(KeyStats))

    price_target = EmbeddedDocumentField(PriceTarget)

    # Price time series
    daily_adjusted_ts = ListField(EmbeddedDocumentField(DailyAdjusted))
