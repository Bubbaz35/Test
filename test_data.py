import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate random test data
num_records = 1000
start_date = datetime(2023, 1, 1)
data = []

for i in range(num_records):
    date = start_date + timedelta(days=random.randint(0, 364))
    profit_loss = random.uniform(-1000, 1000)
    data.append([date.strftime('%Y-%m-%d'), profit_loss])

df = pd.DataFrame(data, columns=['Date', 'Profit/Loss'])
df.to_csv('test_data.csv', index=False)
