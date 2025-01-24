from .logger import get_logger
from functools import cmp_to_key
import pandas
from .query import (
    query_0,
    query_1,
    query_2,
    q0l,
    q1l,
    q2l,
    query_by,
    query_relation_0,
    query_relation_1,
    query_language_relation_0,
    query_language_relation_1,
)
from .shared import write_force
logger = get_logger("movie_finder")
instance_of_any_subclass_of = "wdt:P31/wdt:P279*"


def with_qx(x):
    return """
        with {{
            {query_x}
        }} as %qx
    """.replace("x", f"{x}")


def wikidata_ids_from_csv(path, csv_file):
    df = pandas.read_csv(path)
    data = df.to_dict(orient="records")
    data = [
        x[csv_file].replace('http://www.wikidata.org/entity/', '')
        for x in data
    ]
    def cmp_(a,b):
        return len(a) - len(b)
    cmp_key = cmp_to_key(cmp_)
    data.sort(key=cmp_key)
    return data


def add_query(queries, path, q):
    assert queries.get(path) is None
    queries[path] = q
    path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/query/{path}.sparql"
    logger.info(path.replace("/root", "$HOME"))
    write_force(
        path,
        q,
    )


def get_queries(config):
    queries = {}
    for lang in config['languages']:
        for item_k, v in config['data'].items():
            item_v = config['wikidata_items'][item_k]
            if isinstance(item_v, str):
                add_query(
                    queries,
                    f"{lang}/{item_k}",
                    q0l.format(
                        item_k=item_k,
                        lang=lang,
                        with_q0=with_qx(0).format(
                            query_0=query_0.format(
                                item_k=item_k,
                                item_v=item_v,
                                instance_of_any_subclass_of=instance_of_any_subclass_of,
                            ),
                        ),
                    )
                )
                for field_k, subfields in v.items():
                    if "-by-" in field_k:
                        field_ka = field_k.split("-by-")[0]
                        field_kb = field_k.split("-by-")[1]
                        item_wdt = config['wikidata_fields'][field_ka]
                        with_wdt = config['wikidata_fields'][field_kb]
                        qk = f"{lang}/{item_k}/{field_ka}/by/{field_kb}"
                        csv_file = config['bys'][field_kb]['csv']
                        path = f"/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/{csv_file}.csv"
                        for with_wd in wikidata_ids_from_csv(path, csv_file):
                            add_query(
                                queries,
                                f"{qk}/{with_wd}",
                                query_by.format(
                                    parent=item_k,
                                    instance_of_any_subclass_of=instance_of_any_subclass_of,
                                    parent_wd=item_v,
                                    item_wdt=item_wdt,
                                    item=field_ka,
                                    with_wdt=with_wdt,
                                    with_wd=with_wd,
                                    lang=lang,
                                ),
                            )
                    else:
                        field_v = config['wikidata_fields'][field_k]
                        add_query(
                            queries,
                            f"{lang}/{item_k}/{field_k}",
                            q1l.format(
                                field_k=field_k,
                                lang=lang,
                                with_q0=with_qx(0).format(
                                    query_0=query_0.format(
                                        item_k=item_k,
                                        item_v=item_v,
                                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                                    ),
                                ),
                                with_q1=with_qx(1).format(
                                    query_1=query_1.format(
                                        item_k=item_k,
                                        item_v=item_v,
                                        field_k=field_k,
                                        field_v=field_v,
                                        with_q0="",
                                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                                    ),
                                ),
                            )
                        )
                        for sub_field_k in subfields:
                            sub_field_v = config['wikidata_fields'][sub_field_k]
                            add_query(
                                queries,
                                f"{lang}/{item_k}/{field_k}/{sub_field_k}",
                                q2l.format(
                                    sub_field_k=sub_field_k,
                                    lang=lang,
                                    with_q0=with_qx(0).format(
                                        query_0=query_0.format(
                                            item_k=item_k,
                                            item_v=item_v,
                                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                                        ),
                                    ),
                                    with_q1=with_qx(1).format(
                                        query_1=query_1.format(
                                            item_k=item_k,
                                            item_v=item_v,
                                            field_k=field_k,
                                            field_v=field_v,
                                            with_q0="",
                                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                                        ),
                                    ),
                                    with_q2=with_qx(2).format(
                                        query_2=query_2.format(
                                            item_k=item_k,
                                            item_v=item_v,
                                            field_k=field_k,
                                            field_v=field_v,
                                            sub_field_k=sub_field_k,
                                            sub_field_v=sub_field_v,
                                            with_q0="",
                                            with_q1="",
                                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                                        ),
                                    ),
                                )
                            )
            else:
                add_query(
                    queries,
                    f"{lang}/{item_k}",
                    query_language_relation_0.format(
                        subject=item_k,
                        predicate=item_v['predicate'],
                        object=item_v['object'],
                        language=lang,
                    )
                )
                for field_k, subfields in v.items():
                    add_query(
                        queries,
                        f"{lang}/{item_k}/{field_k}",
                        query_language_relation_1.format(
                            subject=item_k,
                            predicate=item_v['predicate'],
                            object=item_v['object'],
                            language=lang,
                            subject_field_predicate=config['wikidata_fields'][field_k],
                            subject_field=field_k,
                        )
                    )
    for item_k, v in config['data'].items():
        item_v = config['wikidata_items'][item_k]
        if isinstance(item_v, str):
            add_query(
                queries,
                f"{item_k}",
                query_0.format(
                    item_k=item_k,
                    item_v=item_v,
                    instance_of_any_subclass_of=instance_of_any_subclass_of,
                )
            )
            for field_k, subfields in v.items():
                if "-by-" in field_k:
                    # -by- is only useful for labels so far
                    pass
                else:
                    field_v = config['wikidata_fields'][field_k]
                    add_query(
                        queries,
                        f"{item_k}/{field_k}",
                        query_1.format(
                            item_k=item_k,
                            item_v=item_v,
                            field_k=field_k,
                            field_v=field_v,
                            with_q0=with_qx(0).format(
                                query_0=query_0.format(
                                    item_k=item_k,
                                    item_v=item_v,
                                    instance_of_any_subclass_of=instance_of_any_subclass_of,
                                ),
                            ),
                            instance_of_any_subclass_of=instance_of_any_subclass_of,
                        )
                    )
                    for sub_field_k in subfields:
                        sub_field_v = config['wikidata_fields'][sub_field_k]
                        add_query(
                            queries,
                            f"{item_k}/{field_k}/{sub_field_k}",
                            query_2.format(
                                item_k=item_k,
                                item_v=item_v,
                                with_q0=with_qx(0).format(
                                    query_0=query_0.format(
                                        item_k=item_k,
                                        item_v=item_v,
                                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                                    ),
                                ),
                                with_q1=with_qx(1).format(
                                    query_1=query_1.format(
                                        item_k=item_k,
                                        item_v=item_v,
                                        field_k=field_k,
                                        field_v=field_v,
                                        with_q0="",
                                        instance_of_any_subclass_of=instance_of_any_subclass_of,
                                    ),
                                ),
                                field_k=field_k,
                                field_v=field_v,
                                sub_field_k=sub_field_k,
                                sub_field_v=sub_field_v,
                                instance_of_any_subclass_of=instance_of_any_subclass_of,
                            )
                        )
        else:
            add_query(
                queries,
                f"{item_k}",
                query_relation_0.format(
                    subject=item_k,
                    predicate=item_v['predicate'],
                    object=item_v['object'],
                )
            )
            for field_k, subfields in v.items():
                add_query(
                    queries,
                    f"{item_k}/{field_k}",
                    query_relation_1.format(
                        subject=item_k,
                        predicate=item_v['predicate'],
                        object=item_v['object'],
                        subject_field_predicate=config['wikidata_fields'][field_k],
                        subject_field=field_k,
                    )
                )
    return queries
