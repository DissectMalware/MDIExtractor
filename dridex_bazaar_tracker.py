import datetime
import abuse_bazaar_client
import json
import csv
import os
import time
from multiprocessing import Pool
import dridex_extractor
import pyzipper
import sys


def dump_records(api_key, tags, start_date, output_dir):
    bazaar = abuse_bazaar_client.AbuseBazaar(api_key)

    has_seen = set()
    files = []
    header = None
    for tag in tags:
        response = bazaar.query(tag, count=10000)
        response_obj = json.loads(response)
        records = bazaar.summarize_query(response_obj, 'xlsm|xlsx|xlsb')

        if len(records) > 0 and not header:
            header = records[0].keys()

        for record in records:
            if record['sha256'] not in has_seen and datetime.datetime.fromisoformat(record['first_seen']) > start_date:
                files.append(list(record.values()))
                has_seen.add(record['sha256'])

    with open(output_dir, 'w', newline='') as output:
        csv_writer = csv.writer(output)
        csv_writer.writerow(header)
        csv_writer.writerows(files)


def dump_files(api_key, record_file_path, output_dir):
    file_paths = []
    bazaar = abuse_bazaar_client.AbuseBazaar(api_key)
    with open(record_file_path, 'r') as input_file:
        csv_reader = csv.reader(input_file)
        next(csv_reader)
        for record in csv_reader:
            sha256 = record[0]
            print(sha256)
            signature = record[1].lower()
            path = os.path.join(output_dir, signature)
            if not os.path.exists(path):
                os.makedirs(path)

            file_content = bazaar.download(sha256)
            file_path = os.path.join(path, sha256 + '.zip')
            with open(file_path, 'bw') as output_file:
                output_file.write(file_content)
            file_paths.append(file_path)

            time.sleep(1)
    return file_paths


def get_config():
    result = json.loads('{}')
    with open(os.path.join('config', 'config.json'), 'r') as config_file:
        result = json.load(config_file)
    return result


def unzip_file(file_path):
    files = []
    with pyzipper.AESZipFile(file_path, 'r') as zipObj:
        output_dir = os.path.dirname(file_path)
        for file in zipObj.namelist():
            zipObj.extract(file, os.path.dirname(file_path), pwd="infected".encode())
            files.append(os.path.join(output_dir, file))
    return files


def process_file(file_path):
    for file in unzip_file(file_path):
        urls = dridex_extractor.main(file, silent=True)
        with open(file + '.url.txt', 'w') as output:
            output.write(''.join(urls))
            print('\r\n'.join(urls))


def main(output_dir):
    tags = ["Dridex"]
    query_result_path = 'output-{}-{}.csv'.format('-'.join(tags), str(datetime.date.today()))
    config = get_config()
    if 'abuse_bazaar_api_key' in config:
        dump_records(config['abuse_bazaar_api_key'], tags, datetime.datetime.now() - datetime.timedelta(hours=12), query_result_path)
        bazaar_zip_files = dump_files(config['abuse_bazaar_api_key'], query_result_path, output_dir)

        with Pool(config['process_pool_size']) as process:
            process.map(process_file, bazaar_zip_files)


if __name__ == "__main__":
    if len(sys.argv) == 2:
     main(sys.argv[1])
