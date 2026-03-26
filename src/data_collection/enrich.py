import pandas as pd

def enrich_text(df):
    df['text'] = df.apply(lambda row: f"Название: {row['name']}. Категория: {row['category']}. Описание: {row['description']}. Адрес: {row['address']}. Часы работы: {row['opening_hours']}.", axis=1)
    return df

if __name__ == '__main__':
    df = pd.read_csv('../data/poi_moscow_sadovoe.csv')
    df = enrich_text(df)
    df.to_csv('../data/poi_moscow_sadovoe_enriched.csv', index=False)