import configparser


def load_config(filename: str):
    """
    Loads settings from configuration file in the specified path.

    :param filename: path of INI file containing the settings
    :return: folder paths for XLSX files, JSON files containing table schemas,
    output folder for JSONL and GCP URIs
    """
    config = configparser.ConfigParser()
    config.read(filename)

    data_raw = config['local']['raw'].strip('\n')
    data_jsonl = config['local']['jsonl'].strip('\n')
    schemas = config['local']['schemas'].strip('\n')

    project = config['cloud']['project'].strip('\n')
    bucket = config['cloud']['bucket'].strip('\n')
    dataset = config['cloud']['dataset'].strip('\n')

    do_xlsx2jsonl = (config['options']['xlsx2jsonl'].strip('\n') == 'True')
    do_storage = (config['options']['storage'].strip('\n') == 'True')
    do_bigquery = (config['options']['bigquery'].strip('\n') == 'True')

    nlp = (config['nlp']['nlp'].strip('\n') == 'True')

    return data_raw, data_jsonl, schemas, project, bucket, dataset, do_xlsx2jsonl, do_storage, do_bigquery, nlp
