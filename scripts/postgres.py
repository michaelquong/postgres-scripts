import gzip
import logging
import os
import psycopg2
import subprocess
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from urllib import parse
from pathlib import Path
from psycopg2 import sql
from sqlalchemy import URL, create_engine, text

log = logging.getLogger(__name__)
log_level = logging.INFO
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler = logging.StreamHandler()

log.setLevel(log_level)
log_handler.setFormatter(log_format)
log.addHandler(log_handler)


class kind(Enum):
  SOURCE = "source"
  TARGET = 'target'


@dataclass
class PGDetails(ABC):
  username: str = "postgres"
  password: str = ""
  hostname: str = "localhost"
  port: int = 5432
  database: str = "postgres"
  
  @property
  def uri(self) -> URL:
    """
    Connection string for self.database
    """
    return self.create_uri(self.database)
  
  @property
  def postgres_uri(self) -> URL:
    """
    Connection string for postgres database.
    """
    return self.create_uri("postgres")
  
  def create_uri(self, database:str) -> URL:
    """
    database postgres uri connection string
    """
    # return URL.create(
    #   "postgresql",
    #   username=self.username,
    #   password=parse.quote_plus(self.password),
    #   host=self.hostname,
    #   port=self.port,
    #   database=database,
    # )
    return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{database}"

 
@dataclass
class Endpoint(PGDetails):
  _temp_database_postfix:str = field(init=False, default="_restore" )
  endpoint: kind = None
  
  @property
  def backup_filename(self) -> str:
    """
    filename of SQL backup
    """
    return datetime.utcnow().strftime(f"data-{self.database}-%y%m%d_UTC.sql")

  @property
  def temporary_database(self):
    """
    Temporary database name used during data restoration
    """
    if self.endpoint is kind.TARGET:
      return f"{self.database}{self._temp_database_postfix}"
    raise AttributeError("Attribute not applicable to this Endpoint kind.")
  
  @property
  def engine(self):
    """
    Create engine object for postgres database; Mainly for administration tasks.
    """

    
    
    return create_engine(self.postgres_uri, isolation_level="AUTOCOMMIT")
    

@dataclass
class Postgres:
    source: Endpoint
    target: Endpoint
    storage: str = "./"
    
    @property
    def backup_filename(self):
      """
      Full path to backed up SQL file.
      """
      return Path(self.storage) / self.source.backup_filename
    
    def client(self) -> dict:
      """
      Return Postgres Client info of tools.
      """
      return "hi"
    
    def _extract(self, filename:str) -> str:
      out, ext = os.path.splitext(filename)
      
      with gzip.open(filename, "rb") as f:
        with open(out, "wb") as f_out:
          for line in f:
            f_out.write(line)
      return out
    
    def create_database(self)-> str:
      """
      Drop existing database if exist in preparation for new database for migration.
      
      Preserve existing database by restoring to an alternative database name until migration
      activities complete.
      """
      queries = [
        f"DROP DATABASE IF EXISTS {self.target.temporary_database};",
        f"CREATE DATABASE {self.target.temporary_database};",
        f"GRANT ALL PRIVILEGES ON DATABASE {self.target.temporary_database} TO {self.target.username};",
      ] 
      
      with self.target.engine.begin() as connection:
        for q in queries:
          connection.execute(text(q))
      log.info(f"Created {self.target.temporary_database} for data restoration...")
      return self.target.temporary_database 

    def create_backup(self, verbosity:bool=False) -> str:
      """
      Create a Postgres Backup of database.
      """
      cmd = [
        "pg_dump",
        f"--dbname={self.source.uri}", 
        "-Fc", "-f", self.backup_filename
      ]
      if verbosity:
        cmd.append("-v")
      
      _, _, _ = run(cmd=cmd)
      
      log.info(f"Completed backup: {self.backup_filename}")
      return self.backup_filename
        
    def restore_backup(self, input_file:str, verbosity:bool=False) -> None:
      """
      Restore a Postgres database from a backup, <input_file>, into `<database>_restore`
      Once restoration has complete, rename `<database>_restore` to `<database>`
      """
      temporary_db = self.create_database()
      
      cmd = [
        "pg_restore",
        "--no-owner",
        f"--dbname={self.target.create_uri(temporary_db)}",
      ]
      if verbosity:
        cmd.append("-v")
      cmd.append(input_file)
      
      output, _, _ = run(cmd=cmd)
      
      # Rename temporary restore database with existing active database.
      queries = [
        f"DROP DATABASE IF EXISTS {self.target.database};",
        f"ALTER DATABASE {self.target.temporary_database} RENAME TO {self.target.database};",
        f"DROP DATABASE IF EXISTS {self.target.temporary_database};",
      ] 
      
      with self.target.engine.begin() as connection:
        for q in queries:
          connection.execute(text(q))
          
      log.info(f"Promoting to new {self.target.database}...")
      log.info(f"Completed restore")
      return None
      
      

def run(cmd: list) -> tuple:
  """
  run cmd and output process, stdout, stderr as a tuple
  """
  try:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout, stderr = process.communicate()
    if int(process.returncode) != 0:
      log.error(stderr.decode("utf-8"))
      exit(process.returncode)
    if len(stdout.decode('utf-8')) > 0:
      log.info(f"Output: {stdout.decode('utf-8')}")
    
  except Exception as e:
    log.error(f"Error running cmd: `{cmd}`. Error Msg: {e}")
  
  return (process, stdout, stderr)
  