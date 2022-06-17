import glob
import os
import typesense

from typesense.api_call import ObjectNotFound
from acdh_tei_pyutils.tei import TeiReader
from tqdm import tqdm


files = glob.glob('./data/editions/*.xml')
TYPESENSE_API_KEY = os.environ.get("TYPESENSE_API_KEY", "xyz")


client = typesense.Client({
  'nodes': [{
    'host': os.environ.get('TYPESENSE_HOST','localhost'), # For Typesense Cloud use xxx.a1.typesense.net
    'port': os.environ.get('TYPESENSE_PORT', '8108'),      # For Typesense Cloud use 443
    'protocol': os.environ.get('TYPESENSE_PROTOCOL', 'http')   # For Typesense Cloud use https
  }],
  'api_key': TYPESENSE_API_KEY,
  'connection_timeout_seconds': 120
})

try:
    client.collections['bahr-static'].delete()
except ObjectNotFound:
    pass

current_schema = {
    'name': 'bahr-static',
    'fields': [
        {
            'name': 'id',
            'type': 'string'
        },
        {
            'name': 'rec_id',
            'type': 'string'
        },
        {
            'name': 'title',
            'type': 'string'
        },
        {
            'name': 'full_text',
            'type': 'string'
        },
        {
            'name': 'year',
            'type': 'int32',
            'optional': True,
            'facet': True,
        },
        {
            'name': 'persons',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'places',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'orgs',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'works',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
    ]
}

client.collections.create(current_schema)

records = []
for x in tqdm(files, total=len(files)):
    record = {}
    doc = TeiReader(x)
    body = doc.any_xpath('.//tei:body')[0]
    record['id'] = os.path.split(x)[-1].replace('.xml', '')
    record['rec_id'] = os.path.split(x)[-1]
    record['title'] = " ".join(" ".join(doc.any_xpath('.//tei:titleStmt/tei:title[1]//text()')).split())
    date_str = doc.any_xpath('.//@when')[0]
    try:
        record['year'] = int(date_str[:4])
    except ValueError:
        pass
    record['persons'] = [
        " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:person/tei:persName')
    ]
    record['places'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:place[@xml:id]/tei:placeName')
    ]
    record['orgs'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:org[@xml:id]/tei:orgName')
    ]
    record['works'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:listBibl//tei:bibl[@xml:id]/tei:title')
    ]
    record['full_text'] = " ".join(''.join(body.itertext()).split())
    records.append(record)

make_index = client.collections['bahr-static'].documents.import_(records)
print('done with indexing')