root = "Q1914636" # activity
root = "Q12737077" # occupation
root = "Q61788060" # human activity
root = "Q3769299" # human behavior
root = "Q146" # cat
root = "Q2095" # food
root = "Q10675206" # ingredient

root = "Q10675206"

optional = "OPTIONAL"
languages = f"""
    {optional}{{ ?item rdfs:label ?label_en filter (lang(?label_en) = "en"). }}
    {optional}{{ ?item rdfs:label ?label_fr filter (lang(?label_fr) = "fr"). }}
    {optional}{{ ?item rdfs:label ?label_it filter (lang(?label_it) = "it"). }}
    {optional}{{ ?item rdfs:label ?label_es filter (lang(?label_es) = "es"). }}
"""
query = f"""
SELECT distinct
    ?parent_class_up_up_up_up
    ?parent_class_up_up_up
    ?parent_class_up_up
    ?parent_class_up
    ?item ?itemLabel
    ?label_en ?label_fr ?label_it ?label_es
WHERE {{
    {{
        ?item wdt:P279 wd:{root} .
        {languages}
    }}
    union
    {{
        ?item wdt:P279 ?parent_class_up .
        ?parent_class_up wdt:P279 wd:{root} .
        {languages}
    }}
    union
    {{
        ?item                   wdt:P279 ?parent_class_up .
        ?parent_class_up        wdt:P279 ?parent_class_up_up .
        ?parent_class_up_up     wdt:P279 wd:{root} .
        {languages}
    }}
    union
    {{
        ?item                       wdt:P279 ?parent_class_up .
        ?parent_class_up            wdt:P279 ?parent_class_up_up .
        ?parent_class_up_up         wdt:P279 ?parent_class_up_up_up .
        ?parent_class_up_up_up      wdt:P279 wd:{root} .
        {languages}
    }}
    union
    {{
        ?item                       wdt:P279 ?parent_class_up .
        ?parent_class_up            wdt:P279 ?parent_class_up_up .
        ?parent_class_up_up         wdt:P279 ?parent_class_up_up_up .
        ?parent_class_up_up_up      wdt:P279 ?parent_class_up_up_up_up .
        ?parent_class_up_up_up_up      wdt:P279 wd:{root} .
        {languages}
    }}
    SERVICE wikibase:label {{
        bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en,fr,ar,be,bg,bn,ca,cs,da,de,el,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh' .
    }}
}}
"""
