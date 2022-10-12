SELECT distinct
     ?parent_class_up
     ?item ?itemLabel
     ?label_en ?label_fr ?label_it ?label_es
 WHERE {
     {
         ?item wdt:P279* ?parent_class_up .
         ?parent_class_up wdt:P279 wd:Q1914636 .

     OPTIONAL{ ?item rdfs:label ?label_en filter (lang(?label_en) = "en"). }
     OPTIONAL{ ?item rdfs:label ?label_fr filter (lang(?label_fr) = "fr"). }
     OPTIONAL{ ?item rdfs:label ?label_it filter (lang(?label_it) = "it"). }
     OPTIONAL{ ?item rdfs:label ?label_es filter (lang(?label_es) = "es"). }

     }
     SERVICE wikibase:label {
         bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en,fr,ar,be,bg,bn,ca,cs,da,de,el,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh' .
     }
 }
