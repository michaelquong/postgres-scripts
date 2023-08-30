import yaml
from scripts import Postgres, Endpoint, kind

def main():
  with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
  
  # start instance
  pg = Postgres(
      source=Endpoint(endpoint=kind.SOURCE, **config["postgres"]["source"]), 
      target=Endpoint(endpoint=kind.TARGET, **config["postgres"]["target"]),
      storage=config["postgres"]["storage"]["local"]
  )
  output = pg.create_backup(verbosity=True)
  
  pg.restore_backup(input_file=output, verbosity=True)
  
  print(output)
  # pg.restore_backup(input_file=output)
    






if __name__ == "__main__":
    main()