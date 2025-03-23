from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Load data
    portfolio_df = pd.read_excel('data/portfolio_analysis.xlsx')
    screener_df = pd.read_excel('data/stock_analysis.xlsx')
    evaluation_df = pd.read_excel('data/evaluation_results.xlsx')

    return render_template('index.html', 
                           portfolio=portfolio_df.to_dict(orient='records'),
                           screener=screener_df.to_dict(orient='records'),
                           evaluation=evaluation_df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
