transactions = 0

import pandas as pd
import numpy as np
import talib
from datetime import date
from nsepy import get_history

# important variables for indicators
START_DATE = date(2020, 1, 1)
END_DATE = date.today()

# for risk value counting optimization
month = 0
portfolio_ticker_list = []
three_days_window = []

# date list to traverse through the dictionary
date_list = []
try:
    date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
except AttributeError:
    print("AttributeError1 while fetching data for date_list, wait a while...")
    try:
        date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
    except AttributeError:
        print("AttributeError2 while fetching data for date_list, wait a while...")
        try:
            date_list = [str(date) for date in get_history(symbol="SBIN", start=START_DATE, end=END_DATE).index]
        except AttributeError:
            print("AttributeError3 while fetching data for date_list, wait a while...")
print("date_list cleared")

# gathering NSE top100 ticker's list
ticker_list = ["SBIN"] #pd.read_csv("nifty50_csv.csv")['Symbol'].to_list()  # top100 NSE_csv.csv
print("ticker list cleared")


# Capital variables
INITIAL_AMOUNT = 10000
demat_fund = 10000
lowest_demat_price = 10000
invested_amount = 0

# Optimizing variables
    #profit targets
PROFITABILITY_EXPECTANCY_RATE_FIRST = 1.05
PROFITABILITY_EXPECTANCY_RATE_SECOND = 1.1
    #risk percentage
RISK_PERCENTAGE = 2
    #stop-loss
RIGID_STOPLOSS = 5
TRAILING_SL = 7
    #%delivery related
DELIVERY_WINDOW_LENGTH = 10
DELIVERY_PR_FLUCTUATION = 1.1
COUNTING_STOCH_DAYS_AFTER_PRDELIVERY = 7
    #stochastic indecator
STOCH_INTERVAL_DAYS = 14
STOCH_LOWER_BAND = 40
STOCH_HIGHER_BAND = 70


# portfolio Variables
portfolio = {ticker: {"quantity": 0, 'average_trading_price': 0, "highest_traded_closing_price_after_buy": 0, "PNL": [], "crossed_lower_target": False, "crossed_higher_target": False, "delivery_ma_window": [], "delivery_MA": 0, "counting days after buy signal": 0, "buying_signal_date": ""} for ticker in ticker_list}
print("portfoilio cleared")


# raw data for each ticker
raw_data_nse100 = {}
try:
    for ticker in ticker_list:
        ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
        ticker_date_list = []
        try:
            ticker_date_list = [str(date) for date in ticker_dataframe.index]
        except AttributeError:
            print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
            try:
                ticker_date_list = [str(date) for date in ticker_dataframe.index]
            except AttributeError:
                print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError3 while fetching data for ticker_date_list, wait a while...")

        ticker_dataframe["date_list"] = ticker_date_list
        ticker_dataframe.set_index("date_list", inplace=True)
        raw_data_nse100[ticker] = ticker_dataframe

except AttributeError:
    print("AttributeError1 while fetching data for raw_data_nse100, wait a while...")
    try:
        for ticker in ticker_list:
            ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
            ticker_date_list = []
            try:
                ticker_date_list = [str(date) for date in ticker_dataframe.index]
            except AttributeError:
                print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                    try:
                        ticker_date_list = [str(date) for date in ticker_dataframe.index]
                    except AttributeError:
                        print("AttributeError3 while fetching data for ticker_date_list, wait a while...")
            ticker_dataframe["date_list"] = ticker_date_list
            ticker_dataframe.set_index("date_list", inplace=True)
            raw_data_nse100[ticker] = ticker_dataframe

    except AttributeError:
        print("AttributeError2 while fetching data for raw_data_nse100, wait a while...")
        try:
            for ticker in ticker_list:
                ticker_dataframe = get_history(ticker, START_DATE, END_DATE)
                ticker_date_list = []
                try:
                    ticker_date_list = [str(date) for date in ticker_dataframe.index]
                except AttributeError:
                    print("AttributeError1 while fetching data for ticker_date_list, wait a while...")
                    try:
                        ticker_date_list = [str(date) for date in ticker_dataframe.index]
                    except AttributeError:
                        print("AttributeError2 while fetching data for ticker_date_list, wait a while...")
                        try:
                            ticker_date_list = [str(date) for date in ticker_dataframe.index]
                        except AttributeError:
                            print("AttributeError3 while fetching data for ticker_date_list, wait a while...")
                ticker_dataframe["date_list"] = ticker_date_list
                ticker_dataframe.set_index("date_list", inplace=True)
                raw_data_nse100[ticker] = ticker_dataframe
        except AttributeError:
            print("AttributeError3 while fetching data for raw_data_nse100, wait a while...")
print("raw data cleared")

# stochastic for every ticker
stoch14_nse100 = {}
for ticker in ticker_list:
    try:
        stoch14_nse100[ticker] = talib.STOCH(raw_data_nse100[ticker]['High'], raw_data_nse100[ticker]['Low'],
                                             raw_data_nse100[ticker]['Close'], 14)
    except:
        print('Error STOCH 14, fetching data for', ticker)


# counting immediate total invested fund for the given date
def count_currently_invested_amount(portfolio_ticker_list, stdate, enddate):
    stdate_shredded = [int(dmy) for dmy in str(stdate).split("-")]
    enddate_shredded = [int(dmy) for dmy in str(enddate).split("-")]
    invested_amount = 0
    for ticker in portfolio_ticker_list:  # Counting total invested amount by multiplying the current portfolio ticker quantity with the current respective price
        try:  # 'IndexError' exception handling
            current_ticker_price = get_history(symbol=ticker, start=date(stdate_shredded[0], stdate_shredded[1], stdate_shredded[2]),
                        end=date(enddate_shredded[0], enddate_shredded[1], enddate_shredded[2]))['Close'][-1]
            invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
        except AttributeError:
            print("portfolio counting AttributeError1 in", ticker)
            try:  # 'IndexError' exception handling
                current_ticker_price = get_history(symbol=ticker, start=date(stdate_shredded[0], stdate_shredded[1], stdate_shredded[2]),
                            end=date(enddate_shredded[0], enddate_shredded[1], enddate_shredded[2]))['Close'][-1]
                invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
            except AttributeError:
                print("portfolio counting AttributeError2 in", ticker)
                try:  # 'IndexError' exception handling
                    current_ticker_price = get_history(symbol=ticker, start=date(stdate_shredded[0], stdate_shredded[1], stdate_shredded[2]),
                                end=date(enddate_shredded[0], enddate_shredded[1], enddate_shredded[2]))['Close'][-1]
                    invested_amount += current_ticker_price * portfolio[ticker]["quantity"]
                except AttributeError:
                    print("portfolio counting AttributeError3 in", ticker)

        except IndexError:
            print("portfolio counting IndexError in", ticker)

        except KeyError:
            print("portfolio counting KeyError in  ", ticker)

    return invested_amount


print("start survey")

# strategy excecution
for date_index in date_list:

    # five days window
    three_days_window.append(date_index)
    if len(three_days_window) > 3:
        three_days_window.remove(three_days_window[0])
    three_days_window_day_first = three_days_window[0]
    three_days_window_day_last = three_days_window[-1]

    if month == 0:
        # 1% of the total fund
        risking_amount = ((count_currently_invested_amount(portfolio, three_days_window_day_first, three_days_window_day_last) + demat_fund) * RISK_PERCENTAGE) / 100

    if len(three_days_window) > 2:
        for ticker in ticker_list:
            try:

                #counting days to get the stochastic hit after %Delivery signal
                if portfolio[ticker]["counting days after buy signal"] == -1:
                    portfolio[ticker]["counting days after buy signal"] = 1

                if portfolio[ticker]["counting days after buy signal"] > 0:
                    portfolio[ticker]["counting days after buy signal"] += 1

                if portfolio[ticker]["counting days after buy signal"] == COUNTING_STOCH_DAYS_AFTER_PRDELIVERY:
                    portfolio[ticker]["counting days after buy signal"] = 0
                


                current_ticker_price = np.round(raw_data_nse100[ticker]["Close"][date_index], 2)
                current_ticker_delivery = np.round(raw_data_nse100[ticker]["%Deliverble"][date_index], 4)
                current_ticker_stoch_K = np.round(stoch14_nse100[ticker][0][date_index], 2)
                current_ticker_stoch_D = np.round(stoch14_nse100[ticker][1][date_index], 2)
                
                # lowest demat fund register
                if demat_fund < lowest_demat_price:
                    lowest_demat_price = demat_fund

                # for the trailing stop-loss
                if portfolio[ticker]["quantity"] > 0:
                    if current_ticker_price > portfolio[ticker]["highest_traded_closing_price_after_buy"]:
                        portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price
                
                #%Delivery-MA calculation and modification
                if len(portfolio[ticker]["delivery_ma_window"]) < DELIVERY_WINDOW_LENGTH:
                    portfolio[ticker]["delivery_ma_window"].append(current_ticker_delivery)
                
                if len(portfolio[ticker]["delivery_ma_window"]) == DELIVERY_WINDOW_LENGTH:
                    portfolio[ticker]["delivery_MA"] = (sum(portfolio[ticker]["delivery_ma_window"])) / DELIVERY_WINDOW_LENGTH
                    portfolio[ticker]["delivery_ma_window"].remove(portfolio[ticker]["delivery_ma_window"][0])
                    
                if (current_ticker_delivery > (portfolio[ticker]["delivery_MA"] * DELIVERY_PR_FLUCTUATION)) and (portfolio[ticker]["delivery_MA"] > 0):
                    portfolio[ticker]["counting days after buy signal"] = -1
                    
                    portfolio[ticker]["buying_signal_date"] = date_index

                
                # buying rules ------------------------------------------------------------

                # stochastic boolean marking
                if (current_ticker_stoch_K > current_ticker_stoch_D) and (current_ticker_stoch_K >= STOCH_LOWER_BAND) and (current_ticker_stoch_D <= STOCH_LOWER_BAND) and (portfolio[ticker]["counting days after buy signal"] > 0):

                    # stop-loss
                    stoploss_gap = current_ticker_price * (RIGID_STOPLOSS / 100)

                    # qunatity to buy
                    buy_quantity = np.round((risking_amount / stoploss_gap), 0)

                    # buying command
                    if demat_fund >= (buy_quantity * current_ticker_price):
                        # averaging the price
                        portfolio[ticker]["average_trading_price"] = ((portfolio[ticker]["average_trading_price"] * portfolio[ticker]["quantity"]) + (current_ticker_price * buy_quantity)) / (portfolio[ticker]["quantity"] + buy_quantity)

                        # subtract bought amount from the demat amount
                        demat_fund -= (buy_quantity * current_ticker_price)

                        # modifying quantity of the ticker in the portfolio
                        portfolio[ticker]["quantity"] += buy_quantity

                        # taking record of the buy/sell mini statement for the excel sheet
                        portfolio[ticker]["PNL"].append((date_index, "BOUGHT for", current_ticker_price, portfolio[ticker]["average_trading_price"], "signal date: ", portfolio[ticker]["buying_signal_date"], "quantity: ", portfolio[ticker]["quantity"], "HTP: ",portfolio[ticker]["highest_traded_closing_price_after_buy"], "risk amount: ", risking_amount, "current total fund: ", risking_amount * 100))

                        # for the trailing stop-loss
                        if current_ticker_price > portfolio[ticker]["highest_traded_closing_price_after_buy"]:
                            # highest trading price for trailing stop-loss
                            portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price

                        # message statement
                        print(date_index, " BUY -- ", ticker, " Price: ", current_ticker_price, " %K: ", current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ", demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"], " average price: ", portfolio[ticker]["average_trading_price"])


                        # adding ticker into portfolio_list
                        if ticker not in portfolio_ticker_list:
                            portfolio_ticker_list.append(ticker)

                        transactions += 1

                    elif (current_ticker_price * buy_quantity) > demat_fund:

                        portfolio[ticker]["PNL"].append((date_index, "BUYING CHANCE!", current_ticker_price, portfolio[ticker]["average_trading_price"], portfolio[ticker]["quantity"]))


                # selling signals ------------------------------------------------------------
                if portfolio[ticker]["quantity"] > 0:

                    # checking if price crossed PROFITABILITY_EXPECTANCY_RATE_FIRST
                    if current_ticker_price >= (portfolio[ticker]["average_trading_price"] * PROFITABILITY_EXPECTANCY_RATE_FIRST):
                        portfolio[ticker]["crossed_lower_target"] = True

                    # checking if price crossed PROFITABILITY_EXPECTANCY_RATE_SECOND
                    if current_ticker_price >= (portfolio[ticker]["average_trading_price"] * PROFITABILITY_EXPECTANCY_RATE_SECOND):
                        portfolio[ticker]["crossed_higher_target"] = True

                    # price action not crossed PROFITABILITY_EXPECTANCY_RATE_FIRST yet
                    if portfolio[ticker]["crossed_lower_target"] == False:

                        if current_ticker_price < (portfolio[ticker]["highest_traded_closing_price_after_buy"] * (1 - (RIGID_STOPLOSS / 100))):

                            # adding the sold amount into the demat fund
                            demat_fund += current_ticker_price * portfolio[ticker]["quantity"]

                            # taking record of the buy/sell mini statement for the excel sheet
                            portfolio[ticker]["PNL"].append((date_index, "SOLD for", current_ticker_price,portfolio[ticker]["average_trading_price"], "signal date: ", portfolio[ticker]["buying_signal_date"], "PNL: ", ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker]["average_trading_price"],"REASON: Selling by Stop-loss hit", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))

                            # quantity void after sell
                            portfolio[ticker]["quantity"] = 0

                            # atp void after sell
                            portfolio[ticker]["average_trading_price"] = 0

                            # htp void after sell
                            portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                            print(date_index, " SELL ", ticker, " Price: ", current_ticker_price, " %K: ",
                                  current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ",
                                  demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                                  " average price: ", portfolio[ticker]["average_trading_price"],
                                  "REASON: Selling by Stoploss hit")

                            # removing the ticker from the portfolio_ticker_list
                            portfolio_ticker_list.remove(ticker)

                            transactions += 1

                    #price action crossed PROFITABILITY_EXPECTANCY_RATE_FIRST
                    if portfolio[ticker]["crossed_lower_target"] == True:

                        #htp update after achieving the first target level
                        portfolio[ticker]["highest_traded_closing_price_after_buy"] = current_ticker_price

                        # selling by stochastics and PROFITABILITY_EXPECTANCY_RATE_SECOND crossover
                        if (current_ticker_stoch_K < STOCH_HIGHER_BAND) and (current_ticker_stoch_K < current_ticker_stoch_D) and (current_ticker_stoch_D >= STOCH_HIGHER_BAND) and (portfolio[ticker]["crossed_higher_target"] == True):

                            demat_fund += current_ticker_price * portfolio[ticker]["quantity"]

                            portfolio[ticker]["PNL"].append((date_index, "SOLD for", current_ticker_price,portfolio[ticker]["average_trading_price"], "signal date: ", portfolio[ticker]["buying_signal_date"], "PNL: ", ((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) / portfolio[ticker]["average_trading_price"],"REASON: Selling by Stochastic indication", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))

                            portfolio[ticker]["quantity"] = 0

                            portfolio[ticker]["average_trading_price"] = 0

                            portfolio[ticker]["crossed_higher_target"] = False

                            portfolio[ticker]["crossed_lower_target"] = False

                            portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                            print(date_index, " SELL ", ticker, " Price: ", current_ticker_price, " %K: ",
                                  current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ",
                                  demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                                  " average price: ", portfolio[ticker]["average_trading_price"],
                                  "REASON: Selling by Stochastic indication")

                            # removing the ticker from the portfolio_ticker_list
                            portfolio_ticker_list.remove(ticker)

                            transactions += 1

                        # selling according to trailing stop-loss
                        if current_ticker_price < (portfolio[ticker]["highest_traded_closing_price_after_buy"] * (1 - (TRAILING_SL / 100))):

                            demat_fund += current_ticker_price * portfolio[ticker]["quantity"]

                            portfolio[ticker]["PNL"].append((date_index, "SOLD for", current_ticker_price,portfolio[ticker]["average_trading_price"], "signal date: ", portfolio[ticker]["buying_signal_date"], "PNL: ",np.round(((current_ticker_price - portfolio[ticker]["average_trading_price"]) * 100) /portfolio[ticker]["average_trading_price"], 2), "REASON: Hit below Trailing Stop-loss", "HTP: ", portfolio[ticker]["highest_traded_closing_price_after_buy"]))

                            portfolio[ticker]["quantity"] = 0

                            portfolio[ticker]["average_trading_price"] = 0

                            portfolio[ticker]["crossed_higher_target"] = False

                            portfolio[ticker]["crossed_lower_target"] = False

                            portfolio[ticker]["highest_traded_closing_price_after_buy"] = 0

                            print(date_index, " SELL -- ", ticker, " Price: ", current_ticker_price, " %K: ",
                                  current_ticker_stoch_K, " %D: ", current_ticker_stoch_D, "\n Demat fund: ",
                                  demat_fund, "    current ", ticker, "quantity: ", portfolio[ticker]["quantity"],
                                  " average price: ", portfolio[ticker]["average_trading_price"],
                                  "REASON: Hit below Trailing Stop-loss")

                            # removing the ticker from the portfolio_ticker_list
                            portfolio_ticker_list.remove(ticker)

                            transactions += 1


            # 'IndexError', 'KeyError' and 'ValueErrors' are likely to happen so to avoid that, exception handling is used here
            except IndexError:
                print("IndexError in ", ticker)

            except KeyError:
                print("KeyError in ", ticker)

            except ValueError:
                print("ValueError: in ", ticker)

    else:
        print("waiting till 3 days to complete")

    month += 1

    if month >= 30:
        month = 0

# final invested amount counting
invested_amount = count_currently_invested_amount(portfolio, START_DATE, END_DATE)

print("Demat Fund: ", demat_fund, "\n",
      "Invested Fund's Current Value: ", invested_amount, "\n",
      "Total Profit: ", np.round((invested_amount + demat_fund - INITIAL_AMOUNT) * 100 / INITIAL_AMOUNT, 2), "%")

dfportfolio = pd.DataFrame(portfolio).transpose().to_csv("Report_Algorithm-5.csv")

print("lowest demat amount", lowest_demat_price)