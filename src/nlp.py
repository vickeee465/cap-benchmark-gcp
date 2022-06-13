import hu_core_news_lg
import pandas as pd
from tqdm import tqdm


def process_text(model, text_id: str, text: str):
    """
    Performs morphological analysis with sentence segmentation and tokenization on given text.
    The output format is similar to the CoNLL-U format:
    https://universaldependencies.org/format.html

    :param model: loaded language model (HuSpaCy - hu_core_news_lg)
    :param text_id: unique id from the XLSX file containing the texts
    :param text: text to be processed
    :return: Pandas DataFrames of the analyzed sentences and words
    """
    doc = model(text)

    mondat_df = pd.DataFrame()
    conll_szo_df = pd.DataFrame()

    sentence_id = 1
    word_id = 1
    # iterating through sentences
    for sentence in doc.sents:
        mondat_id = sentence_id
        raw_text = sentence.text
        text_id = text_id

        tmp_df = pd.DataFrame(data=[[mondat_id, raw_text, text_id]])
        mondat_df = pd.concat((mondat_df, tmp_df))

        # iterating through tokens
        for token in sentence:
            szo_id = word_id
            szoalak = token.text
            lemma = token.lemma_
            entity_IOB = " ".join([token.ent_iob_, token.ent_type_])
            POS = token.pos_
            morf_analysis = str(token.morph)
            dependencia_el = token.dep_
            mondat_id = sentence_id

            tmp_df = pd.DataFrame(
                data=[[szo_id, szoalak, lemma, entity_IOB, POS, morf_analysis, dependencia_el, mondat_id]])
            conll_szo_df = pd.concat((conll_szo_df, tmp_df))

            word_id += 1
        sentence_id += 1
    return mondat_df, conll_szo_df


def handle_text_analysis(df: pd.DataFrame, path: str):
    """
    Handles NLP analysis of the whole corpus using the HuSpaCy large model (hu_core_news_lg).
    More info: https://github.com/huspacy/huspacy

    :param df: DataFrame containing the texts and metadata
    :param path: output folder of the generated JSONL files
    :return: None
    """
    mondat_columns = ['mondat_id', 'raw_text', 'text_id']
    conll_szo_columns = ['szo_id', 'szoalak', 'lemma', 'entity_IOB', 'POS', 'morf_analysis',
                         'dependencia_el', 'mondat_id']

    mondat_df = pd.DataFrame()
    conll_szo_df = pd.DataFrame()

    # loading NLP model
    model = hu_core_news_lg.load()

    # iterating through texts
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc='   ---> running NLP on text data: ', leave=True,
                           position=0):
        # if index == 50:  # DEBUG
        #     break  # DEBUG

        text = row['text']
        text_id = row['text_id']

        (mondat, conll_szo) = process_text(model, text_id, text)
        mondat_df = pd.concat((mondat_df, mondat), ignore_index=True)

        # "mondat_id" in "conll_szo_df" is not unique by default
        if index > 0:
            mondat_id = conll_szo_df.iloc[-1, -1]
            conll_szo.iloc[:, -1] += mondat_id

        conll_szo_df = pd.concat((conll_szo_df, conll_szo), ignore_index=True)

    # adding column names to dataframes
    mondat_df.columns = mondat_columns
    conll_szo_df.columns = conll_szo_columns

    # "mondat_df" and "conll_szo_df" didn't have a unique id by default
    mondat_df['mondat_id'] = mondat_df.index
    conll_szo_df['szo_id'] = conll_szo_df.index

    # matching "mondat_id" in "mondat_df" and "conll_szo_df"
    conll_szo_df['mondat_id'] -= 1

    # exporting jsonl
    path += "/"
    mondat_df.to_json(path + 'mondat.jsonl', orient="records", lines=True, force_ascii=False)
    conll_szo_df.to_json(path + 'conll_szo.jsonl', orient="records", lines=True, force_ascii=False)
