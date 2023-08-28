import gzip
import logging
import os
import psycopg2
import subprocess
from abc import ABC
from dataclasses import dataclass, field
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


log = logging.getLogger(__name__)
log_level = logging.INFO
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler = logging.StreamHandler()

log.setLevel(log_level)
log_handler.setFormatter(log_format)
log.addHandler(log_handler)


class PGDetails(ABC):
  username: str = "postgres"
  password: str = ""
  hostname: str = "localhost"
  port: int = 5432
  database: str = "postgres"
  
  @property
  def db_uri(self) -> str:
    """
    database postgres uri connection string
    """
    return f"postgresql://{self.username}:{self.password or ''}@{self.hostname}:{self.port}/{self.database}"
  
  def dsn(self, database:str = None) -> dict:
    """
    Return psycopg2 DSN (Data Source Name) connection parameters
    """
    return dict(
      dbname=database or self.database,
      user=self.username,
      password=self.password,
      host=self.hostname,
      port=self.port
    )
 
 
@dataclass
class Endpoint(PGDetails):
  endpoint_type:str
  _restore_database:str = field(init=False, default=None)
  
  def __post_init__(self):
    self._restore_database = f"{self.database}_restore"

  @property
  def restore_db_uri(self) -> str:
      return f"postgresql://{self.username}:{self.password or ''}@{self.hostname}:{self.port}/{self._restore_database}"
  
@dataclass
class Postgres:
    source: Endpoint
    target: Endpoint
    
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
      # create temporary database to accept data migration
      migration_db = self.target.restore_db_uri
      
      conn = self.target.dsn(database="postgres")
      with psycopg2.connect(**conn) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
          queries = [
            # drain activities on migration db
            sql.SQL("SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid() "
                    "AND datname = {}").format(sql.Literal(migration_db)),
            # recreate migration db
            sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Literal(migration_db)),
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(migration_db)),
            # grant privileges
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
              sql.Literal(migration_db), sql.Literal(self.target.username)
            ),
          ]
          
          for q in queries:
            cursor.execute(q)
          
          log.info(f"Created {migration_db}...")
          return migration_db


    def create_backup(self, output_file:str, verbosity:bool=False) -> str:
      """
      Create a Postgres Backup of database.
      """
      cmd = [
        "pg_dump",
        f"--dbname={self.source.db_uri}", 
        "-Fc", "-f", output_file
      ]
      if verbosity:
        cmd.append("-v")
      
      _, _, _ = run(cmd=cmd)
      
      log.info(f"Completed backup: {output_file}")
      return output_file
        
    def restore_backup(self, input_file:str, verbosity:bool=False) -> None:
      """
      Restore a Postgres database from a backup, <input_file>, into `<database>_restore`
      Once restoration has complete, rename `<database>_restore` to `<database>`
      """
      migration_db = self.create_database()
      
      cmd = [
        "pg_restore",
        "--no-owner",
        f"--dbname={self.target.restore_db_uri}",
      ]
      if verbosity:
        cmd.append("-v")
      cmd.append(input_file)
      
      output, _, _ = run(cmd=cmd)
      
      # Rename temporary restore database with existing active database.
      new_db = self.target.database
      
      conn = self.target.dsn(database="postgres")
      with psycopg2.connect(**conn) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor as cursor:
          queries = [
            # Drain activities on active database
            sql.SQL("SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE pid <> pg_backend_pid() "
                    "AND datname = {}").format(sql.Literal(new_db)),
            # drop existing active database
            sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Literal(new_db)),
            # rename migration database as new active database (Replacement)
            sql.SQL("ALTER DATABASE '{}' RENAME '{}'").format(
              sql.Identifier(migration_db), sql.Identifier(new_db)
            )
          ]
          
          for q in queries:
            cursor.execute(q)
          
          log.info(f"Promoting to new {new_db}...")
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
    log.info(f"Output: {stdout.decode('utf-8')}")
    
  except Exception as e:
    log.error(f"Error running cmd: `{cmd}`. Error Msg: {e}")
  
  return (process, stdout, stderr)
  