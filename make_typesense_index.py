import glob
import os
import typesense

from typesense.api_call import ObjectNotFound
from acdh_cfts_pyutils import TYPESENSE_CLIENT as client
from acdh_cfts_pyutils import CFTS_COLLECTION
from acdh_tei_pyutils.tei import TeiReader
from tqdm import tqdm


files = glob.glob('./data/editions/*.xml')


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
cfts_records = []
for x in tqdm(files, total=len(files)):
    cfts_record = {
        'project': 'bahr-static',
    }
    record = {}
    doc = TeiReader(x)
    body = doc.any_xpath('.//tei:body')[0]
    record['id'] = os.path.split(x)[-1].replace('.xml', '')
    cfts_record['id'] = record['id']
    record['rec_id'] = os.path.split(x)[-1]
    cfts_record['rec_id'] = record['rec_id']
    record['title'] = " ".join(" ".join(doc.any_xpath('.//tei:titleStmt/tei:title[1]//text()')).split())
    cfts_record['title'] = record['title']
    date_str = doc.any_xpath('.//@when')[0]
    try:
        record['year'] = int(date_str[:4])
        cfts_record['year'] = int(date_str[:4])
    except ValueError:
        pass
    record['persons'] = [
        " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:person/tei:persName')
    ]
    cfts_record['persons'] = record['persons']
    record['places'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:place[@xml:id]/tei:placeName')
    ]
    cfts_record['places'] = record['places']
    record['orgs'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:org[@xml:id]/tei:orgName')
    ]
    cfts_record['orgs'] = record['orgs']
    record['works'] = [
         " ".join(" ".join(x.xpath('.//text()')).split()) for x in doc.any_xpath('.//tei:back//tei:listBibl//tei:bibl[@xml:id]/tei:title')
    ]
    cfts_record['works'] = record['works']
    record['full_text'] = " ".join(''.join(body.itertext()).split())
    cfts_record['full_text'] = record['full_text']
    records.append(record)
    cfts_records.append(cfts_record)

make_index = client.collections['bahr-static'].documents.import_(records)
print('done with indexing bahr-static')

make_index = CFTS_COLLECTION.documents.import_(cfts_records)

