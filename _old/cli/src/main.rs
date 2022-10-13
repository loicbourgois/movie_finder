use async_recursion::async_recursion;
use clap::{Parser, Subcommand};
use error_chain::error_chain;
use rust_helpers::format_rust;
use rust_helpers::home_dir;
use rust_helpers::lint_rust;
use serde::Deserialize;
// use std::fmt::format;
use rust_helpers::runshellcmd;
use std::fs;
use std::fs::File;
use std::io::Write;
use std::process::Command;
error_chain! {
    foreign_links {
        Io(std::io::Error);
        HttpRequest(reqwest::Error);
    }
}
#[derive(Parser)]
#[clap(name = "dtw")]
#[clap(about = "Down to What CLI", long_about = None)]
struct Cli {
    #[clap(subcommand)]
    command: Commands,
}
#[derive(Subcommand)]
enum Commands {
    /// Data builder commands
    #[clap(subcommand)]
    Dbb(DbbCommands),
    /// Format source code
    Format,
    /// Lint source code
    Lint,
    /// Docker compose for local dev
    Dev,
    /// Query wikidata with `sparqle_query.py`
    Query,
    /// Sparqle commands
    #[clap(subcommand)]
    Sparqle(SparqleCommands),
}
#[derive(Subcommand)]
enum DbbCommands {
    Go,
}
#[derive(Subcommand)]
enum SparqleCommands {
    Tree,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Cli::parse();
    match &args.command {
        Commands::Dbb(subcommand) => match subcommand {
            DbbCommands::Go => {
                go().await?;
                Ok(())
            }
        },
        Commands::Sparqle(subcommand) => match subcommand {
            SparqleCommands::Tree => {
                tree().await?;
                Ok(())
            }
        },
        Commands::Format => {
            format_rust(&[
                &format!("{}/cli/", base_dir()),
                &format!("{}/submodules/rust_helpers", base_dir()),
            ]);
            Ok(())
        }
        Commands::Lint => {
            lint_rust(&[
                &format!("{}/cli/", base_dir()),
                &format!("{}/submodules/rust_helpers", base_dir()),
            ]);
            Ok(())
        }
        Commands::Dev => dev(),
        Commands::Query => query(),
    }
}

fn dev() -> Result<()> {
    runshellcmd(
        Command::new("docker-compose")
            .arg("--file")
            .arg(format!("{}/docker-compose.yml", base_dir()))
            .arg("up")
            .arg("--build")
            .arg("--renew-anon-volumes"),
    );
    Ok(())
}

fn query() -> Result<()> {
    runshellcmd(
        Command::new("docker-compose")
            .arg("--file")
            .arg(format!("{}/docker-compose-tooling.yml", base_dir()))
            .arg("up")
            .arg("--build"),
    );
    Ok(())
}

fn base_dir() -> String {
    return format!("{}/github.com/loicbourgois/downtowhat", home_dir());
}
fn base_dir_local() -> String {
    return format!("{}/github.com/loicbourgois/downtowhat_local", home_dir());
}

#[derive(Debug, Deserialize)]
struct SparqleResponse {
    // head: SparqleHead,
    results: SparqleResults,
}

#[derive(Debug, Deserialize)]
struct SparqleHead {
    // vars: SparqleVars,
}

#[derive(Debug, Deserialize)]
struct SparqleResults {
    bindings: SparqleBindings,
}

// type SparqleVars = Vec<String>;
type SparqleBindings = Vec<SparqleBinding>;

#[derive(Debug, Deserialize)]
struct SparqleBinding {
    item: SparqleItem,
    #[serde(alias = "itemLabel")]
    label: SparqleLabel,
}

#[derive(Debug, Deserialize)]
struct SparqleItem {
    // r#type: String,
    value: String,
}
#[derive(Debug, Deserialize)]
struct SparqleLabel {
    // #[serde(alias = "xml:lang")]
    // lang: Option<String>,
    // r#type: String,
    value: String,
}

async fn go() -> Result<()> {
    let base_url = "https://query.wikidata.org/sparql";
    let querry = "
        SELECT distinct ?item ?itemLabel
        WHERE {
            # instance of / subclass of + job
            # ?item wdt:P31/wdt:P279+  wd:Q192581.
            # subclass of job
            # ?item wdt:P279+ wd:Q192581.
            # subclass of occupation
            # ?item wdt:P279+ wd:Q12737077.
            # food
            #?item wdt:P279* wd:Q2095.
            # ingredient
            #?item wdt:P279* wd:Q10675206.
            ?item (wdt:P279|wdt:P31)+ wd:Q4368298

            # ?item (wdt:P279|wdt:P31)* wd:Q21573184.

            SERVICE wikibase:label {
                bd:serviceParam wikibase:language 'en'.
            }
        }
        limit 20
    ";
    let params = [("query", querry)];
    let client = reqwest::Client::new();
    let res = client
        .post(base_url)
        .form(&params)
        .header("Accept", "application/sparql-results+json")
        .header("User-Agent", "downtowhat/latest (downtowhat.com)")
        .send()
        .await?;
    println!("Status: {}", res.status());
    let body = res.text().await?;
    println!("body ok");
    let r: SparqleResponse = serde_json::from_str(&body).expect("JSON was not well-formatted");
    for (i, binding) in r.results.bindings.iter().enumerate() {
        println!("{} {} {}", i, binding.item.value, binding.label.value);
    }
    Ok(())
}
async fn tree() -> Result<()> {
    let id = "Q1914636";
    let item_path = "activity";
    let item_value = format!("http://www.wikidata.org/entity/{}", id);
    println!("{:045} {}", item_value, item_path);
    let follow = 2;
    tree_subclass_of(id, item_path, follow).await?;
    tree_instance_of(id, item_path, follow).await?;
    Ok(())
}

async fn tree_subclass_of(id: &str, path: &str, follow: i32) -> Result<()> {
    let query_template = "
        SELECT distinct ?item ?itemLabel
        WHERE {
            ?item wdt:P279 wd:ID .
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en' .
            }
        }
    ";
    let file_path = format!("{}/data/tree/{}-c.json", base_dir_local(), id);
    tree_(
        id,
        &format!("{}/c", path),
        follow,
        query_template,
        &file_path,
    )
    .await?;
    Ok(())
}
async fn tree_instance_of(id: &str, path: &str, follow: i32) -> Result<()> {
    // [AUTO_LANGUAGE],en,fr,ar,be,bg,bn,ca,cs,da,de,el,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh
    let query_template = "
        SELECT distinct ?item ?itemLabel ?itemLabel
        WHERE {
            ?item wdt:P31 wd:ID .
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language 'en' .
            }
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language 'en' .
            }
        }
    ";
    let file_path = format!("{}/data/tree/{}-i.json", base_dir_local(), id);
    tree_(
        id,
        &format!("{}/i", path),
        follow,
        query_template,
        &file_path,
    )
    .await?;
    Ok(())
}
#[async_recursion]
async fn tree_(
    id: &str,
    path: &str,
    follow: i32,
    query_template: &str,
    file_path: &str,
) -> Result<()> {
    if follow <= 0 {
        return Ok(());
    };
    let json_str = match fs::read_to_string(file_path) {
        Ok(content) => content,
        Err(_error) => {
            let base_url = "https://query.wikidata.org/sparql";
            let query = query_template.replace("ID", id);
            let client = reqwest::Client::new();
            let res = client
                .post(base_url)
                .form(&[("query", query)])
                .header("Accept", "application/sparql-results+json")
                .header("User-Agent", "downtowhat/latest (downtowhat.com)")
                .send()
                .await?;
            let body = res.text().await?;
            let mut file = File::create(file_path)?;
            write!(file, "{}", body).unwrap();
            body
        }
    };
    let r: SparqleResponse = serde_json::from_str(&json_str).expect("JSON was not well-formatted");
    for (i, binding) in r.results.bindings.iter().enumerate() {
        let item_id = binding
            .item
            .value
            .replace("http://www.wikidata.org/entity/", "");
        let item_path = format!("{}/{}", path, binding.label.value);
        let wikipedia = format!(
            "https://wikipedia.org/wiki/{}",
            binding.label.value.replace(" ", "_")
        );
        println!(
            "{:03}/{:03}, {:042} {:075} {}",
            i + 1,
            r.results.bindings.len(),
            binding.item.value,
            wikipedia,
            item_path
        );
        tree_subclass_of(&item_id, &item_path, follow - 1).await?;
        tree_instance_of(&item_id, &item_path, follow - 1).await?;
    }
    Ok(())
}
