import os
import subprocess
from time import time
from sqlalchemy import create_engine, text

source = os.getenv("SOURCE")
target = os.getenv("TARGET")

engine = create_engine(source)

query = """
    SELECT schema_name
    FROM information_schema.schemata
    WHERE schema_name NOT LIKE 'pg_%'
    AND schema_name NOT LIKE 'information%'
    AND schema_name != 'public'
    ORDER BY schema_name ASC
"""

with engine.begin() as connection:
    result = connection.execute(text(query))
    
schemas = [row[0] for row in result]
backups = []
elapsed_times = []
total = 0

for schema in schemas:
    print(schema)
    dump = [
        "pg_dump",
        f"--dbname={source}",
        f"--schema={schema}"
        "-Fc", "-v", "-w",
        "-f", f"/app/backups/{schema}_data.dump"
    ]
    start = time()
    # subprocess.run(dump)
    end = time()
    
    backups.append(f"/app/backups/{schema}_data.dump")
    elapsed = end-start
    elapsed_times.append(f"Completed: {schema}_data.dump in {elapsed} secs")
    total += elapsed

elapsed_times.append("----------")

for backup in backups:
    print(backup)
    restore = [
        "pg_restore",
        f"--dbname={target}",
        "-v", backup
    ]
    start = time()
    # subprocess.run(restore)
    end = time()
    elapsed = end-start
    elapsed_times.append(f"Restored: {schema}_data.dump in {elapsed} secs")
    total += elapsed
    
for msg in elapsed_times:
    print(msg)
print(f"Completed everything in: {total} secs")