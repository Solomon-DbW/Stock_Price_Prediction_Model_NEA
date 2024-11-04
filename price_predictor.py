import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from datetime import datetime, timedelta
# import seaborn as sns

class StockPricePredictor:
    def __init__(self, stock_symbol: str, prediction_days: int = 60):
        """
        Initialize the stock price predictor.
        
        Args:
            stock_symbol: Stock ticker symbol (e.g., 'AAPL' for Apple)
            prediction_days: Number of previous days to use for prediction
        """
        self.stock_symbol = stock_symbol
        self.prediction_days = prediction_days
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.data = None
        self.scaled_data = None
        self.x_train = None
        self.y_train = None
        
    def fetch_data(self, start_date: str = '2022-01-01'):
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            start_date: Start date for historical data
        """
        try:
            self.data = yf.download(self.stock_symbol, start=start_date, end=datetime.now())
            print(f"Successfully downloaded data for {self.stock_symbol}")
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False
            
    def prepare_data(self):
        """Prepare data for LSTM model."""
        # Scale the closing prices
        self.scaled_data = self.scaler.fit_transform(self.data['Close'].values.reshape(-1, 1))
        
        # Prepare training sequences
        x_train = []
        y_train = []
        
        for x in range(self.prediction_days, len(self.scaled_data)):
            x_train.append(self.scaled_data[x-self.prediction_days:x, 0])
            y_train.append(self.scaled_data[x, 0])
            
        self.x_train = np.array(x_train)
        self.y_train = np.array(y_train)
        self.x_train = np.reshape(self.x_train, 
                                (self.x_train.shape[0], self.x_train.shape[1], 1))
        
    def build_model(self):
        """Build and compile the LSTM model."""
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, 
                 input_shape=(self.x_train.shape[1], 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        
        self.model.compile(optimizer=Adam(learning_rate=0.001),
                         loss='mean_squared_error')
        
        print("Model built successfully!")
        
    def train_model(self, epochs: int = 25, batch_size: int = 32):
        """
        Train the LSTM model.
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        history = self.model.fit(self.x_train, self.y_train, 
                               epochs=epochs, batch_size=batch_size, 
                               validation_split=0.1,
                               verbose=1)
        return history
        
    def predict_next_day(self):
        """Predict the next day's closing price."""
        # Get the last 60 days of data
        last_60_days = self.scaled_data[-self.prediction_days:]
        next_day_input = np.reshape(last_60_days, (1, self.prediction_days, 1))
        
        # Make prediction and inverse transform
        prediction = self.model.predict(next_day_input)
        actual_prediction = self.scaler.inverse_transform(prediction)[0][0]
        
        current_price = self.data['Close'].iloc[-1]
        price_change = actual_prediction - current_price
        percentage_change = (price_change / current_price) * 100
        
        return actual_prediction, price_change, percentage_change
    
    # def predict_increase_date(self, max_days=60):
    #     """
    #     Estimate the date when the stock price will next increase.
        
    #     Args:
    #         max_days: Maximum number of future days to search for a price increase.
        
    #     Returns:
    #         increase_date: Date when an increase is expected, or None if no increase is found.
    #         predicted_price: Predicted price on the increase date.
    #         price_change: Price difference from the current price to the predicted increase price.
    #         percentage_change: Percentage change from the current price to the predicted increase price.
    #     """
    #     # Get the last 60 days of scaled data to initialize the prediction input
    #     last_60_days = self.scaled_data[-self.prediction_days:]
    #     next_day_input = np.reshape(last_60_days, (1, self.prediction_days, 1))

    #     # Get the current price and date
    #     current_price = self.data['Close'].iloc[-1]
    #     current_date = self.data.index[-1]  # Assuming the data index is a DateTimeIndex

    #     # Iterate for a maximum of `max_days` to search for a price increase
    #     for day in range(1, max_days + 1):
    #         # Predict the next day's price
    #         prediction = self.model.predict(next_day_input)
    #         predicted_price = self.scaler.inverse_transform(prediction)[0][0]

    #         # Check if the predicted price is higher than the current price
    #         if predicted_price > current_price:
    #             increase_date = current_date + timedelta(days=day)
    #             price_change = predicted_price - current_price
    #             percentage_change = (price_change / current_price) * 100
                
    #             return increase_date, predicted_price, price_change, percentage_change

    #         # Update for the next prediction day
    #         current_price = predicted_price  # Update current price to the predicted one
    #         last_60_days = np.append(last_60_days[1:], self.scaler.transform([[predicted_price]]), axis=0)
    #         next_day_input = np.reshape(last_60_days, (1, self.prediction_days, 1))

    #     # Return None if no increase is found within max_days
    #     return None, None, None, None

    def evaluate_model(self):
        """Evaluate model accuracy using recent predictions."""
        # Use last 30 days for testing
        test_start = len(self.data) - 30
        test_data = self.scaled_data[test_start - self.prediction_days:]
        
        x_test = []
        y_test = self.scaled_data[test_start:].reshape(-1)
        
        for x in range(self.prediction_days, len(test_data)):
            x_test.append(test_data[x-self.prediction_days:x, 0])
            
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        
        predictions = self.model.predict(x_test)
        predictions = self.scaler.inverse_transform(predictions)
        actual_values = self.scaler.inverse_transform([y_test])
        
        # Calculate metrics
        mse = np.mean((predictions - actual_values.T) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - actual_values.T))
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'predictions': predictions,
            'actual_values': actual_values.T
        }
    
    def plot_predictions(self, evaluation_results):
        """Plot actual vs predicted prices."""
        plt.figure(figsize=(12, 6))
        plt.plot(evaluation_results['actual_values'], 
                label='Actual Prices', color='blue')
        plt.plot(evaluation_results['predictions'], 
                label='Predicted Prices', color='red')
        plt.title(f'{self.stock_symbol} Stock Price Prediction Results')
        plt.xlabel('Time (days)')
        plt.ylabel('Stock Price')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def plot_training_history(self, history):
        """Plot training history."""
        plt.figure(figsize=(12, 6))
        plt.plot(history.history['loss'], label='Training Loss', color='blue')
        plt.plot(history.history['val_loss'], label='Validation Loss', color='red')
        plt.title('Model Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.show()

# predictor = StockPricePredictor(stock_symbol="AAPL")

# # Fetch the latest data
# if predictor.fetch_data(start_date='2023-01-01'):  # Adjust start_date as needed
#     predictor.prepare_data()
#     predictor.build_model()
#     predictor.train_model()

# # Predict when the price will increase
# increase_date, predicted_price, price_change, percentage_change = predictor.predict_increase_date(max_days=60)

# if increase_date:
#     print(f"Price is expected to increase on {increase_date.date()} to {predicted_price:.2f}")
#     print(f"Change: {price_change:.2f} ({percentage_change:.2f}%)")
# else:
#     print("No price increase expected within the specified future days.")

