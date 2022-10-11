# downtowhat

```sh
docker-compose \
  --file $HOME/github.com/loicbourgois/downtowhat/docker-compose.yml \
  up --build
```

```sh
alias d="cargo run --release --manifest-path $HOME/github.com/loicbourgois/downtowhat/cli/Cargo.toml -- "
d help
```
