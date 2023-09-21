import pandas as pd


def price_initialise(file_path):
    df = pd.read_csv(file_path)

    # remove NaN
    df['price'] = df['price'].fillna(0)

    # min-max normalization
    df['price'] = (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())

    # 1 is the best price, 0 the worse one
    df['price'] = 1 - df['price']

    # transform in a dictionary in the form { item: 1- normalized_price, ...}
    payment = pd.Series(df.price.values, index=df.asin).to_dict()

    return payment
