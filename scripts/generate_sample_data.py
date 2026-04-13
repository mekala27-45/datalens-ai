"""Generate sample datasets for DataLens AI demo mode."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
DATA_DIR = Path(__file__).parent.parent / "data" / "samples"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_ecommerce():
    """Generate e-commerce orders dataset (~3000 rows)."""
    categories = {
        "Electronics": ["Laptop", "Phone", "Tablet", "Headphones", "Smartwatch", "Camera"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Shoes", "Hat"],
        "Home": ["Lamp", "Chair", "Table", "Rug", "Pillow", "Vase"],
        "Sports": ["Bike", "Racket", "Ball", "Gloves", "Mat", "Weights"],
    }
    regions = ["North", "South", "East", "West"]
    statuses = ["Completed", "Completed", "Completed", "Pending", "Cancelled"]

    rows = []
    start_date = datetime(2024, 1, 1)
    for i in range(1, 3001):
        cat = random.choice(list(categories.keys()))
        product = random.choice(categories[cat])
        price = {
            "Electronics": random.uniform(50, 1500),
            "Clothing": random.uniform(15, 200),
            "Home": random.uniform(20, 500),
            "Sports": random.uniform(10, 300),
        }[cat]
        qty = random.randint(1, 5)
        days = random.randint(0, 545)
        date = start_date + timedelta(days=days)
        rows.append({
            "order_id": f"ORD-{i:05d}",
            "order_date": date.strftime("%Y-%m-%d"),
            "product": product,
            "category": cat,
            "quantity": qty,
            "unit_price": round(price, 2),
            "total_amount": round(price * qty, 2),
            "region": random.choice(regions),
            "status": random.choice(statuses),
            "customer_id": f"CUST-{random.randint(1, 500):04d}",
        })

    path = DATA_DIR / "ecommerce_orders.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {path}")


def generate_climate():
    """Generate world climate dataset (~2400 rows)."""
    cities = [
        ("New York", "USA", "North America"),
        ("London", "UK", "Europe"),
        ("Tokyo", "Japan", "Asia"),
        ("Sydney", "Australia", "Oceania"),
        ("Mumbai", "India", "Asia"),
        ("Berlin", "Germany", "Europe"),
        ("Sao Paulo", "Brazil", "South America"),
        ("Cairo", "Egypt", "Africa"),
        ("Toronto", "Canada", "North America"),
        ("Singapore", "Singapore", "Asia"),
    ]
    rows = []
    for city, country, continent in cities:
        base_temp = {
            "New York": 12, "London": 11, "Tokyo": 15, "Sydney": 18,
            "Mumbai": 27, "Berlin": 10, "Sao Paulo": 20, "Cairo": 22,
            "Toronto": 7, "Singapore": 27,
        }[city]
        for year in range(2020, 2025):
            for month in range(1, 13):
                seasonal = 8 * (1 if month in (6, 7, 8) else (-1 if month in (12, 1, 2) else 0))
                if continent == "Oceania":
                    seasonal = -seasonal
                temp = base_temp + seasonal + random.uniform(-3, 3)
                rain = max(0, random.gauss(80, 40) + (20 if month in (6, 7, 8, 9) else -10))
                humidity = max(20, min(100, random.gauss(65, 15)))
                rows.append({
                    "city": city,
                    "country": country,
                    "continent": continent,
                    "year": year,
                    "month": month,
                    "avg_temp_c": round(temp, 1),
                    "rainfall_mm": round(rain, 1),
                    "humidity_pct": round(humidity, 1),
                })

    path = DATA_DIR / "world_climate.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {path}")


def generate_stocks():
    """Generate stock prices dataset (~2500 rows)."""
    tickers = [
        ("AAPL", "Apple", "Technology"),
        ("GOOGL", "Google", "Technology"),
        ("MSFT", "Microsoft", "Technology"),
        ("AMZN", "Amazon", "Consumer"),
        ("JPM", "JPMorgan", "Finance"),
        ("JNJ", "Johnson & Johnson", "Healthcare"),
        ("XOM", "ExxonMobil", "Energy"),
        ("PG", "Procter & Gamble", "Consumer"),
        ("NVDA", "NVIDIA", "Technology"),
        ("TSLA", "Tesla", "Automotive"),
    ]
    rows = []
    start = datetime(2024, 1, 1)
    for ticker, company, sector in tickers:
        base_price = {
            "AAPL": 180, "GOOGL": 140, "MSFT": 370, "AMZN": 155,
            "JPM": 170, "JNJ": 155, "XOM": 100, "PG": 150,
            "NVDA": 500, "TSLA": 240,
        }[ticker]
        price = base_price
        for day in range(250):
            date = start + timedelta(days=day)
            if date.weekday() >= 5:
                continue
            change = random.gauss(0.001, 0.02)
            price = max(10, price * (1 + change))
            high = price * (1 + abs(random.gauss(0, 0.01)))
            low = price * (1 - abs(random.gauss(0, 0.01)))
            volume = int(random.gauss(50_000_000, 20_000_000))
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "ticker": ticker,
                "company": company,
                "sector": sector,
                "open": round(price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(price * (1 + random.gauss(0, 0.005)), 2),
                "volume": max(1000, volume),
            })

    path = DATA_DIR / "stock_prices.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {path}")


def generate_hr():
    """Generate HR employees dataset (1000 rows)."""
    depts = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    titles = {
        "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead", "DevOps Engineer"],
        "Marketing": ["Marketing Analyst", "Content Manager", "SEO Specialist", "Brand Manager"],
        "Sales": ["Sales Rep", "Account Executive", "Sales Manager", "BDR"],
        "HR": ["HR Generalist", "Recruiter", "HR Manager", "People Ops"],
        "Finance": ["Financial Analyst", "Accountant", "Controller", "FP&A Manager"],
        "Operations": ["Operations Analyst", "Project Manager", "Logistics Coord", "COO Staff"],
    }
    education = ["High School", "Bachelor's", "Master's", "PhD"]
    genders = ["Male", "Female", "Non-binary"]

    rows = []
    start = datetime(2015, 1, 1)
    for i in range(1, 1001):
        dept = random.choice(depts)
        title = random.choice(titles[dept])
        exp_years = random.randint(0, 20)
        base = {"Engineering": 95000, "Marketing": 70000, "Sales": 65000,
                "HR": 65000, "Finance": 80000, "Operations": 70000}[dept]
        salary = base + exp_years * random.randint(2000, 5000) + random.randint(-10000, 10000)
        hire = start + timedelta(days=random.randint(0, 3300))
        rows.append({
            "employee_id": f"EMP-{i:04d}",
            "department": dept,
            "job_title": title,
            "hire_date": hire.strftime("%Y-%m-%d"),
            "salary": round(salary, 0),
            "bonus": round(salary * random.uniform(0, 0.15), 0),
            "performance_score": round(random.uniform(1, 5), 1),
            "satisfaction_score": round(random.uniform(1, 5), 1),
            "age": random.randint(22, 62),
            "gender": random.choice(genders),
            "education": random.choices(education, weights=[10, 50, 30, 10])[0],
        })

    path = DATA_DIR / "hr_employees.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {path}")


if __name__ == "__main__":
    generate_ecommerce()
    generate_climate()
    generate_stocks()
    generate_hr()
    print("\nAll sample datasets generated!")
