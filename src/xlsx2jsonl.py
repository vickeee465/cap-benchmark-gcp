import os

import pandas as pd
from tqdm import tqdm

from nlp import handle_text_analysis


def xlsx2jsonl(input_folder: str, output_folder: str, nlp: bool, table_dict: dict):
    """
    Converts CAP data from .xlsx to .jsonl.

    :param input_folder: path of folder containing XLSX files
    :param output_folder:path of folder containing JSONL files
    :param nlp: switch for NLP analysis
    :param table_dict: dictionary containing file and table names
    :return: None
    """
    input_folder += "/"
    output_folder += "/"
    files = os.listdir(input_folder)
    files = [file for file in files if file.endswith(".xlsx") and file.split('.')[0] in table_dict]

    # iterates through files in folder path
    for file in tqdm(files, desc='1. Converting files in ' + os.path.abspath(input_folder)):
        # party_name_full_hun.xlsx contains multiple sheets
        sheet = int(file.startswith("party_name_full"))
        df = pd.read_excel(input_folder + file, sheet_name=sheet)

        # converting pandas datetime to string
        # otherwise to_json would convert datetimes to int
        df = df.assign(**df.select_dtypes(['datetime']).astype(str).to_dict('list'))

        # date and time format in text_jav was not consistent
        if file.startswith('text_jav'):
            df['exact_date'] = df['exact_date'].astype(str).str.replace(' 00:00:00', '')
            df['exact_date'] = df['exact_date'].str.strip('.')
            df['exact_date'] = df['exact_date'].str.replace('.', '-', regex=False)
            df['video_felszolalas_ido'] = df['video_felszolalas_ido'].astype(str)

        # quote marks break the json structure, so we have to use escape characters
        # we also have to remove unnamed columns and forbidden characters in column names
        df = df.replace('"', '\"', regex=True)
        df.columns = df.columns.str.replace(' ', '')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.replace({'NaT': None, 'NA': None, 'nan': None, 'NaN': None, '########': None}, regex=False)

        # running NLP
        if nlp:
            if file.startswith('text'):
                handle_text_analysis(df, output_folder)

        # saving json file
        df.to_json(output_folder + table_dict[file.split('.')[0]] + '.jsonl', orient="records", lines=True,
                   force_ascii=False)
