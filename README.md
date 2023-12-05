# movie_finder


```sh
$HOME/github.com/loicbourgois/movie_finder/commands/run.sh
$HOME/github.com/loicbourgois/movie_finder/commands/test.sh
open http://127.0.0.1:9000
$HOME/github.com/loicbourgois/movie_finder/commands/deploy.sh
$HOME/github.com/loicbourgois/movie_finder/commands/tail_raw.sh
$HOME/github.com/loicbourgois/movie_finder/commands/remote_logs.sh


$HOME/github.com/loicbourgois/movie_finder/commands/build_data.sh
$HOME/github.com/loicbourgois/movie_finder/database/go.sh
$HOME/github.com/loicbourgois/movie_finder/database_client/go.sh
```


## Sources

- https://www.omdb.org/en/us/content/Help:DataDownload 
- wikidata

```sh
cd $HOME/github.com/loicbourgois/movie_finder_local/data_v2 \
    && curl https://www.omdb.org/data/movie_links.csv.bz2 -O \
    && bzip2 -d movie_links.csv.bz2
    && curl https://www.omdb.org/data/image_ids.csv.bz2 -O \
    && bzip2 -d image_ids.csv.bz2
    && curl https://www.omdb.org/data/movie_references.csv.bz2 -O \
    && bzip2 -d movie_references.csv.bz2    

cd $HOME/github.com/loicbourgois/movie_finder_local/data_v2 \
    && curl https://www.omdb.org/data/category_names.csv.bz2 -O \
    && bzip2 -d category_names.csv.bz2

cd $HOME/github.com/loicbourgois/movie_finder_local/data_v2 \
    && curl https://www.omdb.org/data/movie_categories.csv.bz2 -O \
    && bzip2 -d movie_categories.csv.bz2

cd $HOME/github.com/loicbourgois/movie_finder_local/data_v2 \
    && curl https://www.omdb.org/data/all_categories.csv.bz2 -O \
    && bzip2 -d all_categories.csv.bz2
```
