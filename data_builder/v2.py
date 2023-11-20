def query_to_file(path, query):
    args = urllib.parse.urlencode({
        'query': query,
        'format': 'json'
    })
    r = requests.get(f"{endpoint_url}?{args}")
    write_force(path, r.text)


def pull_data_v2():
    data_path = f"{os.environ['HOME']}/github.com/loicbourgois/movie_finder_local/data_v2"
    withs = {
        "director": common.with_director,
        "creator": common.with_creator,
        "producer": common.with_producer,
    }
    media_types = {
        "film": common.film,
        "television_series": common.television_series,
    }
    for wk, wv in withs.items():
        for media_types_k, media_types_v in media_types.items():
            query_to_file(
                f"{data_path}/label/{media_types_k}/{wk}.raw",
                f"""
                    SELECT ?{wk} ?{wk}_label (lang(?{wk}_label) as ?lang)
                    WHERE {{
                        ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                        ?{media_types_k} {wv} ?{wk} .
                        ?{wk} rdfs:label ?{wk}_label filter (lang(?{wk}_label) = "en").
                    }}
                    {common.limit}
                """
            )
            query_to_file(
                f"{data_path}/relation/{media_types_k}/{wk}.raw",
                f"""
                    SELECT ?{media_types_k} ?{wk}
                        WHERE {{
                            ?{media_types_k} {common.instance_of_any_subclass_of} {media_types_v} .
                            ?{media_types_k} {wv} ?{wk} .
                        }}
                    {common.limit}
                """
            )


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], '')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, 'w') as f:
        f.write(content)