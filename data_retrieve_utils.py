import os
import datetime
from datetime import date

from alpha_vantage.timeseries import TimeSeries
from iexfinance.refdata import get_symbols
from iexfinance.stocks import Stock

from data_models import DailyAdjusted, KeyStats, StockDocument


def get_us_symbols():
    all_symbols = get_symbols()
    us_symbols = []
    for symbol_dict in all_symbols:
        if symbol_dict['isEnabled'] is not True:
            continue
        if symbol_dict['region'] != 'US' or symbol_dict['currency'] != 'USD':
            continue
        us_symbols.append(symbol_dict)
    return us_symbols


def populate_us_symbols_in_db():
    us_symbols = get_us_symbols()
    print(len(us_symbols))
    for symbol_dict in us_symbols:
        if not StockDocument.objects(symbol=symbol_dict['symbol']):
            stock_document = StockDocument(symbol=symbol_dict['symbol'],
                name=symbol_dict['name'],
                exchange=symbol_dict['exchange'])
            stock_document.save()


def populate_key_stats(gap_days):
    for stock_document in StockDocument.objects:
        # Update key stats just once per gap_days. 
        # Use 0 to enforce a latest update.
        if stock_document.latest_key_stats is not None \
            and stock_document.latest_key_stats.query_date.date() \
                + datetime.timedelta(days=gap_days) >= datetime.date.today():
            continue

        # Retrieve key stats data from IEX.
        stock = Stock(stock_document.symbol)
        key_stats = stock.get_key_stats()

        # Update key stats fields in db.
        key_stats_document = KeyStats(query_date=datetime.date.today())

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


def get_historical_daily_adjusted_ts(symbol, output_format, output_size):
    ts = TimeSeries(key=os.getenv('ALPHA_VANTAGE_KEY'), output_format=output_format)
    daily_adjusted_ts, _ = ts.get_daily_adjusted(symbol, outputsize=output_size)
    return daily_adjusted_ts


def get_top_market_cap_stocks(top_size):
    return StockDocument.objects().order_by('-latest_key_stats.market_cap')[:top_size]    


def populate_historical_daily_adjusted_for_market_top_500():
    for stock_document in get_top_market_cap_stocks(500):
        full_daily_adjusted_ts = \
            get_historical_daily_adjusted_ts(stock_document.symbol, 'pandas', 'full')

        dates_to_save = []
        for time_stamp, daily_adjusted_df in full_daily_adjusted_ts.iterrows():
            query_date = time_stamp.date()
            if stock_document.daily_adjusted_ts is None \
                or stock_document.daily_adjusted_ts[-1].date.date() < query_date:
                daily_adjusted = DailyAdjusted(time_stamp.date())
                daily_adjusted.open_price = daily_adjusted_df.get('1. open')
                daily_adjusted.high = daily_adjusted_df.get('2. high')
                daily_adjusted.low = daily_adjusted_df.get('3. low')
                daily_adjusted.close_price = daily_adjusted_df.get('4. close')
                daily_adjusted.adjusted_close_price = daily_adjusted_df.get('5. adjusted close')
                daily_adjusted.volume = daily_adjusted_df.get('6. volume')
                daily_adjusted.dividend = daily_adjusted_df.get('7. dividend amount')
                daily_adjusted.split_coefficient = daily_adjusted_df.get('8. split coefficient')
                dates_to_save.append(daily_adjusted)

        for daily_adjusted in dates_to_save[::-1]:
            stock_document.daily_adjusted_ts.append(daily_adjusted)
        stock_document.save()


