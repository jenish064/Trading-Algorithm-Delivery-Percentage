# Trading-Algorithm-Delivery-Percentage

Algorithm-5
-----------

Trading Vehicle and Trade Objective:
Equity Swings

Indicators:
	Market Condition Indicator (to identify the markate trend, range and volatility):
	- Exponential Moving Average-200
	
	Area of value (where might potential buy/sell opportunity come in):
	- Exponential Moving Average-50
	- Stochastic-14

	Exit Strategy BY Stop-loss:
	- Exponential Moving Average-100
	- Trailing Stoploss

Rules:
	Buying:
	- Stochastic %K line value > Stochastic %D line value, AND
	- Stochastic %K line value >= lowest stochastic point, AND
	- Stochastic %D line value <= lowest stochastic point
	- Stochastic boolean tick == True
		- Exponential Moving Average-50 >= Exponential Moving Average-200, AND
		- Exponential Moving Average-50 >= Exponential Moving Average-100, AND
		- Latest trading price > above Exponential Moving Average-50, AND
		- Demat fund >= Latest trading price

		- Apply 1% risk strategy
		- quantity according to the current Stoploss: Exponential Moving Average-100

	Selling:
	use crossed_lower_target boolean and crossed_higher_target boolean
	- Latest trading price <= (Average purchase price * profitability expectancy rate first level)
	- crossed_lower_target == False
//profitability expectancy rate first level, i.e.: ~1.07
		- If Current Exponential Moving Average-100 > Buying Exponential Moving Average-100, AND
		- crossed_lower_target == False
			- If Latest trading price < current Exponential Moving Average-100
			
	- Latest trading price > (Average purchase price * profitability expectancy rate first level)
	- didnt_cross_lower_target == False


			- Stochastic %K line value < Stochastic %D line value, AND
			- Stochastic %K line value < highest stochastic point, AND
			- Stochastic %D line value >= highest stochastic point
	OR
		Stop-loss:
		- Latest trading price, below Exponential Moving Average-50(with risk percrntage ema50), OR
		- Exponential Moving Average-50 <= Exponential Moving Average-200(with risk percrntage ema200), OR
		- Below Trailing Stop-loss
		//- Latest trading price, below by R% of stock purchase value // %R = Risk percentage
	
    Quantity:
    - Decision according to Risk capacity and available fund
