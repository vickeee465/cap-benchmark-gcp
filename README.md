# cap-benchmark-gcp
These simple scripts can...

1. Convert XLSX to newline-delimited JSON.
2. Upload data to Cloud Storage.
3. Create external tables in BigQuery from data in Cloud Storage.

### Prerequisites
* existing project on [Google Cloud Platform](https://cloud.google.com/).
* APIs enabled
  * [BigQuery API](https://console.cloud.google.com/apis/api/bigquery.googleapis.com)
  * [BigQuery Connection API](https://console.cloud.google.com/apis/api/bigqueryconnection.googleapis.com)
  * [Storage API](https://console.cloud.google.com/apis/api/storage.googleapis.com)  
* private key for a Google Cloud Service Account
  * open [Creditentials](https://console.cloud.google.com/apis/credentials)
  * create/open a service account
  * go to KEYS
  * ADD KEY > Create new key
  * in the dialog window create a JSON key
  * place the JSON file in the same folder as the script
  * rename it to "gcp_key.json"
* for the NLP script you have to download a [HuSpaCy](https://github.com/huspacy/huspacy) model
  * the larger model is recommended (hu_core_news_lg)
  * you can do this quickly the following way:
  ```
  pip install https://huggingface.co/huspacy/hu_core_news_lg/resolve/main/hu_core_news_lg-any-py3-none-any.whl
  ```

### Usage
You can modify the parameters in config.ini, which is structured the following way:

#### [local]

| parameter | expected string                               |
|-----------|----------------------------------------------|
| raw       | folder containing raw XLSX data (relative/absolute path)              |
| json      | output folder for newline-delimited JSON (relative/absolute path)    |
| schemas   | folder containing schema information as JSON (relative/absolute path)|


#### [cloud]

| parameter | expected string            |
|-----------|---------------------------|
| project   | GCP project ID          |
| bucket    | Cloud Storage bucket name |
| dataset   | BigQuery dataset name     |

#### [options]

| parameter  | expected string                                     |
|------------|-----------------------------------------------------|
| xlsx2jsonl | True/False (turns conversion on/off)                |
| storage    | True/False (turns Cloud Storage upload on/off)      |
| bigquery   | True/False (turns BigQuery table generation on/off) |

#### [nlp]

| parameter | expected string                         |
|-----------|-----------------------------------------|
| nlp       | True/False (turns text analysis on/off) |


### Schema information
Schemas are loaded from JSON files.
Table structure is almost identical to [cap_pilot_benchmark_xlsx_json](https://github.com/poltextlab/cap_pilot_benchmark_sql_json).

#### cap_kod

| name       | type    | mode     |
| ---------- | ------- | -------- |
| cap_id     | INTEGER | REQUIRED |
| nev_angol  | STRING  | NULLABLE |
| nev_magyar | STRING  | NULLABLE |

#### conll_kod

| name           | type    | mode     |
| -------------- | ------- | -------- |
| szo_id         | INTEGER | REQUIRED |
| szoalak        | STRING  | NULLABLE |
| lemma          | STRING  | NULLABLE |
| entity_IOB     | STRING  | NULLABLE |
| POS            | STRING  | NULLABLE |
| morf_analysis  | STRING  | NULLABLE |
| dependencia_el | STRING  | NULLABLE |
| mondat_id      | INTEGER | NULLABLE |

#### felszolalas

| name                  | type    | mode     |
| --------------------- | ------- | -------- |
| text_id               | INTEGER | REQUIRED |
| text_type             | INTEGER | NULLABLE |
| exact_date            | DATE    | NULLABLE |
| cycle_number          | INTEGER | NULLABLE |
| parliamentary_id      | STRING  | NULLABLE |
| text                  | STRING  | NULLABLE |
| napirendi_pont        | STRING  | NULLABLE |
| video_felszolalas_ido | STRING  | NULLABLE |
| video_feszolalas_url  | STRING  | NULLABLE |
| felszolalas_url       | STRING  | NULLABLE |
| tokenszam             | STRING  | NULLABLE |
| major_topic           | STRING  | NULLABLE |
| COVID                 | STRING  | NULLABLE |
| text_id_old           | STRING  | NULLABLE |

#### kepviselo

| name             | type    | mode     |
| ---------------- | ------- | -------- |
| parliamentary_id | STRING  | REQUIRED |
| surname          | STRING  | NULLABLE |
| first_name       | STRING  | NULLABLE |
| birth_year       | FLOAT   | NULLABLE |
| birth_place      | STRING  | NULLABLE |
| sex              | INTEGER | NULLABLE |
| death_date       | FLOAT   | NULLABLE |
| death_place      | STRING  | NULLABLE |
| PERSON_POS       | INTEGER | NULLABLE |
| change_name      | STRING  | NULLABLE |
| surname_new      | STRING  | NULLABLE |
| surname_from     | DATE    | NULLABLE |
| id_old           | STRING  | NULLABLE |

#### mondat

| name      | type    | mode     |
| --------- | ------- | -------- |
| mondat_id | INTEGER | REQUIRED |
| raw_text  | STRING  | NULLABLE |
| text_id   | STRING  | NULLABLE |

#### parlamenti_ciklus

| name             | type    | mode     |
| ---------------- | ------- | -------- |
| cycle_number     | INTEGER | REQUIRED |
| cycle_years_from | INTEGER | NULLABLE |
| cycle_years_to   | INTEGER | NULLABLE |
| cycle_from       | DATE    | NULLABLE |
| cycle_to         | DATE    | NULLABLE |

#### part

| name                      | type    | mode     |
| ------------------------- | ------- | -------- |
| party_id                  | INTEGER | REQUIRED |
| party_name_full_HUN       | STRING  | NULLABLE |
| party_name_full_HUN_from  | DATE    | NULLABLE |
| party_name_full_HUN_to    | DATE    | NULLABLE |
| party_name2_full_HUN      | STRING  | NULLABLE |
| party_name2_full_HUN_from | DATE    | NULLABLE |
| party_name2_full_HUN_to   | DATE    | NULLABLE |
| party_name3_full_HUN      | STRING  | NULLABLE |
| party_name_full3_HUN_from | DATE    | NULLABLE |
| party_name_full3_HUN_to   | DATE    | NULLABLE |