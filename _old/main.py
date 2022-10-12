print("start")
import sys
import os
from SPARQLWrapper import SPARQLWrapper, JSON
from .data_builders import (
    human_activity,
    action,
    activity,
    occupation,
    professions,
    social_status,
)
data_builders = (
    # human_activity,
    # action,
    # activity,
    occupation,
    #professions,
    social_status,
)

endpoint_url = "https://query.wikidata.org/sparql"
data = f"{os.environ['HOME']}/github.com/loicbourgois/downtowhat_local/data"

def get_results(endpoint_url, query):
    # TODO better user agent; see https://w.wiki/CX6
    user_agent = "downtowhat/latest (downtowhat.com)"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


for data_builder in data_builders:
    print(f"[ start ] {data_builder.name}")
    results = get_results(endpoint_url, data_builder.query)
    lines = [data_builder.header]
    for result in results["results"]["bindings"]:
        lines.append(data_builder.line(result))
    with open(f"{data}/{data_builder.name}.csv", "w") as file:
        file.write("\n".join(lines))
    print(f"[  end  ] {data_builder.name}")
