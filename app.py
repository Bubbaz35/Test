from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        daily_profit_loss = df.groupby('Date').agg({'Profit/Loss': 'sum'}).reset_index()
        df['YearMonth'] = df['Date'].dt.to_period('M')
        monthly_profit_loss = df.groupby('YearMonth').agg({'Profit/Loss': 'sum'}).reset_index()
        monthly_profit_loss['YearMonth'] = monthly_profit_loss['YearMonth'].astype(str)
        return render_template('results.html', profit_loss_data=daily_profit_loss.to_dict(orient='records'), monthly_profit_loss_data=monthly_profit_loss.to_dict(orient='records'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
