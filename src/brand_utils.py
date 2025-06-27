import pandas as pd

def load_brands(path="brands.csv"):
    brands_df = pd.read_csv(path)
    return brands_df['brand'].dropna().str.lower().unique().tolist()

def find_brands_in_text(text, brands):
    text_lower = text.lower()
    return [brand for brand in brands if brand in text_lower]