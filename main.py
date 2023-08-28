import configparser
from pathlib import Path
from scripts import Postgres, Endpoint

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    # build configuration
    cfg = config["source"]
    src = Endpoint(
        endpoint_type="source",
        username=cfg["username"],
        password=cfg["password"],
        hostname=cfg["hostname"],
        port=cfg["port"],
        database=cfg["database"],
    )
    cfg = config["target"]
    tgt = Endpoint(
        endpoint_type="target",
        username=cfg["username"],
        password=cfg["password"],
        hostname=cfg["hostname"],
        port=cfg["port"],
        database=cfg["database"],
    )
    
    fullpath = Path(config["storage"]["local"]) / "data.sql"
    
    # start instance
    pg = Postgres(source=src, target=tgt)
    
    print(pg.client())
    # output = pg.create_backup(output_file=str(fullpath))
    
    # pg.restore_backup(input_file=output)
    






if __name__ == "__main__":
    main()