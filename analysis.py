"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_DIR = Path("output")

def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Could not reach {url}: {exc.__class__.__name__} - check your connection.")
        return []
    if response.status_code != 200:
        print(f"Request failed: {url} returned status {response.status_code}.")
        return []
    try:
        return response.json()
    except ValueError:
        print(f"Request failed: {url} did not return valid JSON.")
        return []

def explore(record, indent: int = 0) -> None:
    """Print nested dictionary keys and list contents with their types."""
    pad = "  " * indent

    if isinstance(record, dict):
        for key, value in record.items():
            print(f"{pad}{key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore(value, indent + 1)

    elif isinstance(record, list):
        for item in record:
            print(f"{pad}- {type(item).__name__}")
            if isinstance(item, (dict, list)):
                explore(item, indent + 1)
def _tld(email: str) -> str:
    """Top-level domain of an email address: 'Sincere@april.biz' -> 'biz'."""
    return email.split("@")[-1].lower().rsplit(".", 1)[-1]

def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for c in customers:
        geo = c["address"]["geo"]
        rows.append({
            "customer_id": c["id"],
            "name": c["name"],
            "username": c["username"],
            "email": c["email"],
            "email_domain": _tld(c["email"]),
            "phone": c["phone"],
            "city": c["address"]["city"],
            "zipcode": c["address"]["zipcode"],
            "latitude": float(geo["lat"]),
            "longitude": float(geo["lng"]),
            "company": c["company"]["name"],
            "website": c["website"],
        })
    return rows

def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}
    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1
    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers by email top-level domain."""
    counts = {}

    for c in customers:
        email = c.get("email", "")

        if "@" in email and "." in email.split("@")[-1]:
            tld = _tld(email)
            counts[tld] = counts.get(tld, 0) + 1

    return dict(
        sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)

def plot_distribution(counts: dict[str, int], path: Path) -> None:
    """Save a labelled chart of the distribution to path."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(counts.keys()), list(counts.values()), color="Blue")
    ax.set_title(f"Customer distribution ({path.stem})")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of customers")
    ax.set_yticks(range(0, max(counts.values()) + 1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
 
    customers = get_customers()
    if not customers:
        raise SystemExit("No data retrieved - stopping.")
    print(f"Fetched {len(customers)} customers.\n")
 
    print("--- Structure of one record ---")
    explore(customers[0])
 
    rows = extract_attributes(customers)
 
    cities = unique_cities(customers)
    print(f"\nUnique cities: {len(cities)} | Customers: {len(customers)}")
    if len(cities) == len(customers):
        print("Every customer is in a different city, so marketing has no city clusters to target.")
    else:
        print("Some cities have several customers, so marketing can run city-level campaigns there.")
 
    by_city = city_counts(customers)
    by_domain = email_domain_counts(customers)
    print("\nCustomers per city:")
    for city, n in by_city.items():
        print(f"  {city}: {n}")
    print("\nCustomers per email domain (TLD):")
    for tld, n in by_domain.items():
        print(f"  {tld}: {n}")
 
    df = to_dataframe(rows)
    print(f"\nDataFrame shape: {df.shape}")
    print(df.dtypes)
    print(df["email_domain"].value_counts().to_dict())
    print(by_domain)
    assert df["city"].value_counts().to_dict() == by_city
    pandas_counts = df["email_domain"].value_counts().to_dict()
    print("pandas:", pandas_counts)
    print("mine:  ", by_domain)
    assert pandas_counts == by_domain
    assert df["email_domain"].value_counts().to_dict() == by_domain
    print("\nvalue_counts() agrees with the hand-written counts.")
 
    df.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    city_df = pd.DataFrame(
    list(by_city.items()),
    columns=["city", "customer_count"]
)

city_df = city_df.sort_values(
    by=["customer_count", "city"],
    ascending=[False, True]
)

city_df.to_csv(
    OUTPUT_DIR / "city_counts.csv",
    index=False
)

most_common_city, most_common_count = sorted(
    by_city.items(),
    key=lambda item: (-item[1], item[0])
)[0]

print(f"Customers retrieved : {len(customers)}")
print(f"Unique cities       : {len(cities)}")
print(f"Most common city    : {most_common_city} ({most_common_count})")
print(f"Email domains       : {by_domain}")

plot_distribution(by_city, OUTPUT_DIR / "customer_distribution.png")
plot_distribution(by_domain, OUTPUT_DIR / "email_domain_distribution.png")
print(f"Chart saved to      : {OUTPUT_DIR / 'customer_distribution.png'}")
print(f"\nSaved CSVs and charts to {OUTPUT_DIR}/")