#!/bin/bash
# Initialize the database with schema and test data

# Wait for services to be ready
echo "Waiting for MongoDB and Chroma to be ready..."
sleep 10

# Run the database initialization script
echo "Initializing database..."
docker exec rpger-backend python /app/init_db.py --with-test-data --retry 5 --retry-delay 5

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo "Database initialization completed successfully!"
else
    echo "Database initialization failed. Check the logs for details."
    exit 1
fi

echo "Database is ready for use."
