from bigquery_utils import create_cap_tables
from config import load_config
from storage_utils import upload_cap_data
from xlsx2jsonl import xlsx2jsonl

# the script requires hu_core_news_lg:
# pip install https://huggingface.co/huspacy/hu_core_news_lg/resolve/main/hu_core_news_lg-any-py3-none-any.whl

if __name__ == '__main__':
    # loading config
    path_raw, path_jsonl, path_schemas, project, \
    bucket, dataset, options_xlsx2jsonl, options_storage, options_bigquery, nlp = load_config('../config.ini')

    table_dict = {
        'CAP_CODE': 'cap_kod',
        'text_jav': 'felszolalas',
        'demo_kész': 'kepviselo',
        'cycle_kész': 'parlamenti_ciklus',
        'party_name_full_hun': 'part',
        'mondat': 'mondat',
        'conll_szo': 'conll_szo'
    }

    if options_xlsx2jsonl:
        xlsx2jsonl(path_raw, path_jsonl, nlp, table_dict)
    if options_storage:
        upload_cap_data(path_jsonl, bucket)
    if options_bigquery:
        create_cap_tables(bucket, project, dataset, path_schemas)
