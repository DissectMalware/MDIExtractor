import json
import urllib.request


class AbuseBazaar:
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def download(sha256):
        res = ""
        url = "https://mb-api.abuse.ch/api/v1/"
        post_data_template = "query=get_file&sha256_hash={}"

        post_data = post_data_template.format(sha256)
        request = urllib.request.Request(url, post_data.encode('ascii'), method="POST")
        with urllib.request.urlopen(request) as response:
            res = response.read()

        return res

    @staticmethod
    def query(query_str, count=1000):
        res = ""
        url = "https://mb-api.abuse.ch/api/v1/"
        post_data_template = "query=get_taginfo&tag={}&limit={}"

        post_data = post_data_template.format(query_str, count)
        request = urllib.request.Request(url, post_data.encode('ascii'), method="POST")
        with urllib.request.urlopen(request) as response:
            res = response.read()

        return bytearray(res).decode('ascii')

    @staticmethod
    def summarize_query(query_response, filter='*'):
        records = []
        for entry in query_response['data']:
            if filter != '*':
                filter = filter.lower()
                if entry['file_type'].lower() in filter.split('|'):
                    records.append({
                        'sha256': entry['sha256_hash'],
                        'signature': entry['signature'] if entry['signature'] else 'UNKNOWN',
                        'first_seen': entry['first_seen'],
                        'file_type_mime': entry['file_type_mime']
                    })
        return records
