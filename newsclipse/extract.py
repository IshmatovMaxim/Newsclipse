import requests
#from pprint import pprint

from newsclipse.core import calais_key


def extract_entities(text):
    URL = 'http://api.opencalais.com/tag/rs/enrich'
    headers = {
        'x-calais-licenseID': calais_key,
        'content-type': 'text/raw',
        'accept': 'application/json'
    }
    res = requests.post(URL, headers=headers,
                        data=text.encode('utf-8'))
    data = res.json()
    for k, v in data.items():
        _type = v.get('_type')
        if _type in ['Person', 'Organization', 'Company']:
            aliases = set([v.get('name')])
            for instance in v.get('instances', [{}]):
                alias = instance.get('exact')
                if alias is not None and len(alias) > 3:
                    aliases.add(alias)
            yield {
                'title': v.get('name'),
                'aliases': list(aliases),
                'offset': v.get('instances', [{}])[0].get('offset'),
                'card': 'entity',
                'type': _type
            }
