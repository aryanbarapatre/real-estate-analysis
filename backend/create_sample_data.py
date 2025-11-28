import csv
import os
from pathlib import Path

# Create data directory if it doesn't exist
BASE_DIR = Path(__file__).resolve().parent.parent
data_dir = os.path.join(BASE_DIR, 'data')
os.makedirs(data_dir, exist_ok=True)

# Sample real estate data
areas = ['Wakad', 'Aundh', 'Ambegaon Budruk', 'Akurdi', 'Hinjewadi', 'Baner', 'Kothrud']
years = [2020, 2021, 2022, 2023, 2024]

# Create CSV file
csv_path = os.path.join(data_dir, 'real_estate_data.csv')
excel_path = os.path.join(data_dir, 'real_estate_data.xlsx')

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write headers
    writer.writerow(['Year', 'Area', 'Price', 'Demand', 'Size'])
    
    # Write data
    for area in areas:
        base_price = 5000 + (abs(hash(area)) % 3000)  # Varying base prices
        base_demand = 50 + (abs(hash(area)) % 30)  # Varying base demand
        
        for year in years:
            # Simulate price growth (8% per year)
            year_index = year - 2020
            price = base_price * (1.08 ** year_index) + (abs(hash(f"{area}{year}")) % 1000)
            
            # Simulate demand fluctuations
            demand = base_demand + (year_index * 5) + (abs(hash(f"{area}{year}")) % 20)
            
            # Property size (800-2000 sqft)
            size = 1000 + (abs(hash(f"{area}{year}")) % 1200)
            
            writer.writerow([
                year,
                area,
                round(price, 2),
                round(demand, 1),
                round(size, 1)
            ])

print(f"Sample CSV file created at: {csv_path}")
print(f"Total rows: {len(areas) * len(years)}")
print(f"Areas: {', '.join(areas)}")
print(f"Years: {min(years)} - {max(years)}")
print(f"\nNote: To convert to Excel, install openpyxl and pandas, then run:")
print(f"  pip install openpyxl pandas")
print(f"  python -c \"import pandas as pd; df = pd.read_csv('{csv_path}'); df.to_excel('{excel_path}', index=False)\"")
