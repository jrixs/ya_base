from etl.load import bulk_load


def datasort_filmwork(data) -> dict:
    try_keys = ("id", "imdb_rating", "genres", "title", "description",
                "directors_names", "actors_names", "writers_names",
                "directors", "actors", "writers")
    ret_data = {}

    for line in data:
        id = line['fw_id']

        if id in ret_data:
            if line['genre'] not in ret_data[id]['genres']:
                ret_data[id]['genres'].append(line['genre'])

            if line['role'] == 'director' and line['full_name'] \
               not in ret_data[id]['directors_names']:
                ret_data[id]['directors_names'].append(line['full_name'])
                ret_data[id]['directors'].append({'id': line['id'],
                                                  'name': line['full_name']})

            if line['role'] == 'actor' and line['full_name'] \
               not in ret_data[id]['actors_names']:
                ret_data[id]['actors_names'].append(line['full_name'])
                ret_data[id]['actors'].append({'id': line['id'],
                                               'name': line['full_name']})

            if line['role'] == 'writer' and line['full_name'] \
               not in ret_data[id]['writers_names']:
                ret_data[id]['writers_names'].append(line['full_name'])
                ret_data[id]['writers'].append({'id': line['id'],
                                                'name': line['full_name']})

        else:
            id = line['fw_id']
            line = dict(line)
            line['imdb_rating'] = line['rating']
            line['genres'] = [line['genre']]
            line['directors_names'] = list()
            line['actors_names'] = list()
            line['writers_names'] = list()
            line['directors'] = list()
            line['actors'] = list()
            line['writers'] = list()

            if line['role'] == 'director':
                line['directors_names'].append(line['full_name'])
                line['directors'].append({'id': line['id'],
                                          'name': line['full_name']})

            if line['role'] == 'actor':
                line['actors_names'].append(line['full_name'])
                line['actors'].append({'id': line['id'],
                                       'name': line['full_name']})

            if line['role'] == 'writer':
                line['writers_names'].append(line['full_name'])
                line['writers'].append({'id': line['id'],
                                        'name': line['full_name']})

            line['id'] = id
            line = {k: v for k, v in line.items() if k in try_keys}

            ret_data[id] = line

    return ret_data


def datasort_genres(data) -> dict:
    try_keys = ("id", "genre", "films")
    ret_data = {}

    for line in data:
        id = line['g_id']

        if id in ret_data:
            if line['fw_id'] not in [_['id'] for _ in ret_data[id]['films']]:
                ret_data[id]['films'].append({
                    'id': line['fw_id'],
                    'title': line['title'],
                    'imdb_rating': line['rating']
                })
        else:
            id = line['g_id']
            line = dict(line)
            line['id'] = id
            line['genre'] = line['genre']
            line['films'] = [{
                'id': line['fw_id'],
                'title': line['title'],
                'imdb_rating': line['rating']
            }]

            line = {k: v for k, v in line.items() if k in try_keys}

            ret_data[id] = line

    return ret_data


def send_to_es(index_name: str, data: dict) -> bool:
    result: list = []
    for uuid in data:
        result.append({
            "index": {
                "_index": index_name,
                "_id": uuid
                }})
        result.append(data[uuid])
    return bulk_load(result)


def transform_filmwork(data):
    data = [__ for _ in data for __ in _]
    data_filmwork = datasort_filmwork(data)
    data_ganres = datasort_genres(data)

    return all([
        send_to_es(index_name='movies', data=data_filmwork),
        send_to_es(index_name='genres', data=data_ganres)
    ])
