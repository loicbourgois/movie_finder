
from .runcmd import runcmd_list


# https://www.omdb.org/en/us/content/Help:DataDownload
def omdb_pull(config):
    omdb_folder = "/root/github.com/loicbourgois/movie_finder_local/data_v3/csv/omdb"
    runcmd_list(["mkdir", "-p", omdb_folder])
    for item in config['omdb'].keys():
        url = f"https://www.omdb.org/data/{item}.csv.bz2"
        file = f"{item}.csv.bz2"
        runcmd_list(["curl", url, "-O"], cwd=omdb_folder)
        runcmd_list(["rm", file.replace(".csv.bz2", ".csv")], cwd=omdb_folder)
        runcmd_list(["bzip2", "-d", file], cwd=omdb_folder)
