"""Writes data/demo_reviews.csv: ~500 synthetic reviews spread over 14 months,
so the charts, trends and seasonal views have something to show.

Upload it with the "These rows are sample data" box ticked. Run from the project root:
    python scripts/generate_demo_data.py
"""
import csv
import random
from datetime import date, timedelta

random.seed(7)
PRODUCTS = [('Lipstick A', 'Brand A', 'Lipstick', 0.7), ('Lipstick B', 'Brand B', 'Lipstick', 0.5),
            ('Lipstick C', 'Brand C', 'Lipstick', 0.35), ('Foundation A', 'Brand C', 'Foundation', 0.6),
            ('Foundation B', 'Brand A', 'Foundation', 0.45), ('Kajal A', 'Brand B', 'Kajal', 0.65),
            ('Face Cream A', 'Brand D', 'Skincare', 0.55)]
POS = ['Love the colour and it feels lovely', 'Lasts all day, great quality', 'Beautiful shade, very happy with it',
       'Smooth texture and a great finish', 'Perfect match and good value', 'Absolutely love it, would buy again',
       'Lovely scent and creamy texture', 'Premium packaging and wonderful colour']
NEG = ['Looks lovely but it does not last long', 'Shade is different from the photo and I am disappointed',
       'Too expensive for the quality', 'Delivery was late and the bottle was damaged', 'Terrible quality, it faded quickly',
       'Smells strange and the texture is sticky', 'Fake product, I want my money back', 'Poor packaging and the cap broke']
NEU = ['It is okay, nothing special', 'Average product, does the job', 'Arrived on time, standard packaging']

start = date(2025, 8, 1)
rows = []
for i in range(1, 501):
    name, brand, cat, p_pos = random.choice(PRODUCTS)
    d = start + timedelta(days=random.randint(0, 425))
    r = random.random()
    text = random.choice(POS) if r < p_pos else random.choice(NEG) if r < p_pos + (1 - p_pos) * 0.8 else random.choice(NEU)
    rows.append([f'D{i:04d}', name, brand, cat, text, d.isoformat()])
rows.sort(key=lambda x: x[5])
with open('data/demo_reviews.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['review_id', 'product_name', 'brand', 'category', 'review_text', 'review_date'])
    w.writerows(rows)
print('Wrote data/demo_reviews.csv with', len(rows), 'rows')
