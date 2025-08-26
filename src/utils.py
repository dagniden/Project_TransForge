import pandas as pd

def read_excel(filename: str) -> list[dict]:
    data = pd.read_excel(filename)
    return data.to_dict('records')