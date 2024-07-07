
def query_builder_movies(data: dict) -> dict:

    body = {
        "_source": ["id", "imdb_rating", "genres", "title"],
        "query": {"bool": {"must": [], "filter": []}},
        "size": int(data['page_size']),
        "from": (int(data['page']) - 1) * int(data['page_size']),
    }

    if data.get('search'):
        search_query = {"multi_match": {
            "query": data.get('search'), "fields": ["*"]}}
        body["query"]["bool"]["must"].append(search_query)

    if data.get('order_by'):
        order = "desc" if data.get('order_by').startswith("-") else "asc"
        sort_by = data.get('order_by').lstrip("-")
        body["sort"] = [{sort_by: {"order": order}}]

    return body


def query_builder_persons(data: dict) -> dict:

    if data['name']:
        order = "desc" if data['name'].startswith('-') else "asc"
    else:
        order = None

    body = {
            "_source": ["id", "full_name"],
            "query": {"bool": {
                "must": [{"match": {
                    "full_name": data['name']}}] if data['name'] else [{"match_all": {}}]
                }
            },
            "sort": [{"full_name": {"order": order}} if order else {}],
            "size": int(data['page_size']),
            "from": (int(data['page']) - 1) * int(data['page_size']),
        }

    return body
