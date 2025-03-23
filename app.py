from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Load data
    portfolio_df = pd.read_excel('data/portfolio_analysis.xlsx')
    screener_df = pd.read_excel('data/stock_analysis.xlsx')
    evaluation_df = pd.read_excel('data/evaluation_results.xlsx')

    # Example for chart data: assuming you want to plot stock prices over time.
    # For simplicity, using a dummy list for stock prices. Replace this with actual data.
    chart_data = {
        "labels": ["January", "February", "March", "April", "May", "June", "July"],
        "prices": [150, 160, 170, 165, 180, 175, 190]  # Replace with your real data
    }

    # Render the template with data
    return render_template('index.html', 
                           portfolio=portfolio_df.to_dict(orient='records'),
                           screener=screener_df.to_dict(orient='records'),
                           evaluation=evaluation_df.to_dict(orient='records'),
                           chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
