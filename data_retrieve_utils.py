import os
from datetime import date

from alpha_vantage.timeseries import TimeSeries
from iexfinance.refdata import get_symbols
from iexfinance.stocks import Stock

from data_models import DailyAdjusted, KeyStats, StockDocument


def get_us_symbols():
    all_symbols = get_symbols()
    us_symbols = []
    for symbol in all_symbols:
        if symbol['isEnabled'] is not True:
            continue
        if symbol['region'] != 'US' or symbol['currency'] != 'USD':
            continue
        us_symbols.append(symbol)
    return us_symbols


def populate_us_symbols_in_db():
    us_symbols = get_us_symbols()
    for symbol in us_symbols:
        stock = StockDocument(symbol=symbol['symbol'],
            name=symbol['name'], exchange=symbol['exchange'])
        stock.save()


def populate_key_stats():
    for stock_document in StockDocument.objects:
        # Key stats updates once per day.
        if stock_document.latest_key_stats == date.today():
            continue

        # Retrieve key stats data from IEX.
        stock = Stock(stock_document.symbol)
        key_stats = stock.get_key_stats()

        # Update key stats fields in db.
        key_stats_document = KeyStats(query_date=date.today())

        key_stats_document.market_cap = key_stats.get('marketcap')
        key_stats_document.pe_ratio = key_stats.get('peRatio')
        key_stats_document.beta = key_stats.get('beta')

        key_stats_document.ttm_eps = key_stats.get('ttmEPS')
        key_stats_document.ttm_dividend_rate = key_stats.get('ttmDividendRate')
        key_stats_document.dividend_yield = key_stats.get('dividendYield')
        key_stats_document.next_dividend_date = key_stats.get('nextDividendDate')
        key_stats_document.ex_dividend_date = key_stats.get('exDividendDate')
        key_stats_document.next_earnings_date = key_stats.get('nextEarningsDate')

        key_stats_document.week_52_high = key_stats.get('week52high')
        key_stats_document.week_52_low = key_stats.get('week52low')
        key_stats_document.week_52_change = key_stats.get('week52change')
        
        key_stats_document.avg_10_volume = key_stats.get('avg10Volume')
        key_stats_document.avg_30_volume = key_stats.get('avg30Volume')

        key_stats_document.day_200_movingavg = key_stats.get('day200MovingAvg')
        key_stats_document.day_50_movingavg = key_stats.get('day50MovingAvg')

        key_stats_document.max_change_percent = key_stats.get('maxChangePercent')
        key_stats_document.year_5_change_percent = key_stats.get('year5ChangePercent')
        key_stats_document.year_2_change_percent = key_stats.get('year2ChangePercent')
        key_stats_document.year_1_change_percent = key_stats.get('year1ChangePercent')
        key_stats_document.ytd_change_percent = key_stats.get('ytdChangePercent')
        key_stats_document.month_6_change_percent = key_stats.get('month6ChangePercent')
        key_stats_document.month_3_change_percent = key_stats.get('month3ChangePercent')
        key_stats_document.month_1_change_percent = key_stats.get('month1ChangePercent')
        key_stats_document.day_30_change_percent = key_stats.get('day30ChangePercent')
        key_stats_document.day_5_change_percent = key_stats.get('day5ChangePercent')

        stock_document.latest_key_stats = key_stats_document
        stock_document.key_stats_ts.append(key_stats_document)
        stock_document.save()


def get_historical_daily_adjusted_ts(stock):
    ts = TimeSeries(key=os.getenv('ALPHA_VANTAGE_KEY'),
        output_format='pandas')
    full_daily_adjusted_ts, metadata = ts.get_daily_adjusted(stock.symbol)