#!/bin/bash -e

# Start timing the execution of the entire script
start_time=$(date +%s)

echo "Starting backup..."
start_pgdump=$(date +%s)
pg_dump --dbname="$SOURCE" -w -Fc  -v -f "$FILENAME"
sleep 10
end_pgdump=$(date +%s)

echo "Starting restore..."
start_pgrestore=$(date +%s)
pg_restore --dbname="$TARGET" -v "$FILENAME"
sleep 10
end_pgrestore=$(date +%s)

end_time=$(date +%s)

pgdump_duration=$((end_pgdump - start_pgdump))
echo "pg_dump took $pgdump_duration seconds."
pgrestore_duration=$((end_pgrestore - start_pgrestore))
echo "pg_restore took $pgrestore_duration seconds."
total_duration=$((end_time - start_time))
echo "Total script execution time: $total_duration seconds."
