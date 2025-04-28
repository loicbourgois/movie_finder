query_relation_0 = """
    select ?{subject}
    where {{
        ?a wdt:P279* {object}.
        ?{subject} {predicate} ?a.
    }}
"""

query_relation_1 = """
    select ?{subject} ?{subject_field}
    where {{
        ?a wdt:P279* {object}.
        ?{subject} {predicate} ?a.
        ?{subject} {subject_field_predicate} ?{subject_field}.
    }}
"""

query_language_relation_0 = """
    select ?{subject} ?{subject}_label (lang(?{subject}_label) as ?lang)
    where {{
        ?a wdt:P279* {object}.
        ?{subject} {predicate} ?a.
        ?{subject} rdfs:label ?{subject}_label filter (lang(?{subject}_label) = "{language}").
    }}
"""

query_language_relation_1 = """
    select ?{subject_field} ?{subject_field}_label (lang(?{subject_field}_label) as ?lang)
    with {{
        select distinct ?{subject_field}
        where {{
            ?a wdt:P279* {object}.
            ?{subject} {predicate} ?a.
            ?{subject} {subject_field_predicate} ?{subject_field}.
        }}
    }} as %q1
    where {{
        include %q1
        ?{subject_field} rdfs:label ?{subject_field}_label filter (lang(?{subject_field}_label) = "{language}").
    }}
"""


query_0 = """
SELECT distinct ?{item_k}
WHERE {{
    ?{item_k} {instance_of_any_subclass_of} {item_v} .
}}
"""
query_1 = """# {item_k} -.-> {field_k}
SELECT distinct ?{item_k} ?{field_k}
{with_q0}
WHERE {{
    include %q0
    ?{item_k} {field_v} ?{field_k} .
}}
"""
query_2 = """# {item_k}__{field_k} -.-> {sub_field_k}
select distinct ?{field_k} ?{sub_field_k}
{with_q0}
{with_q1}
where {{
    include %q1
    ?{field_k} {sub_field_v} ?{sub_field_k} .
}}
"""
query_by = """
    SELECT ?{item} ?{item}_label (lang(?{item}_label) as ?lang)
    with {{
        SELECT distinct ?{item}
        WHERE {{
            ?{parent} {instance_of_any_subclass_of} {parent_wd} .
            ?{parent} {item_wdt} ?{item} .
            ?{item} {with_wdt} wd:{with_wd} .
        }}
    }} as %q
    WHERE {{
        include %q
        ?{item} rdfs:label ?{item}_label filter (lang(?{item}_label) = "{lang}").
    }}
"""

q0l = """
SELECT ?{item_k} ?{item_k}_label (lang(?{item_k}_label) as ?lang)
{with_q0}
WHERE {{
    include %q0
    ?{item_k} rdfs:label ?{item_k}_label filter (lang(?{item_k}_label) = "{lang}").
}}
"""
q1l = """
SELECT ?{field_k} ?{field_k}_label (lang(?{field_k}_label) as ?lang)
{with_q0}
{with_q1}
with {{
    SELECT distinct ?{field_k}
    WHERE {{
        include %q1
    }}
}} as %q
WHERE {{
    include %q
    ?{field_k} rdfs:label ?{field_k}_label filter (lang(?{field_k}_label) = "{lang}").
}}
"""
q2l = """
SELECT ?{sub_field_k} ?{sub_field_k}_label (lang(?{sub_field_k}_label) as ?lang)
{with_q0}
{with_q1}
{with_q2}
with {{
    SELECT distinct ?{sub_field_k}
    WHERE {{
        include %q2
    }}
}} as %q
WHERE {{
    include %q
    ?{sub_field_k} rdfs:label ?{sub_field_k}_label filter (lang(?{sub_field_k}_label) = "{lang}").
}}
"""
