#!/bin/bash
# Import test data into the RPGer database

# Wait for services to be ready
echo "Waiting for MongoDB to be ready..."
sleep 10

# Run the validation script first
echo "Validating schema and test data..."
docker exec rpger-backend python /app/validate_db.py
if [ $? -ne 0 ]; then
    echo "Validation failed. Please fix the issues before importing data."
    exit 1
fi

# Run the import script with options to skip Chroma
echo "Importing test data..."
docker exec rpger-backend python /app/import_test_data.py --skip-chroma --skip-embeddings
if [ $? -ne 0 ]; then
    echo "Import failed. Check the logs for details."
    exit 1
fi

echo "Database import completed successfully!"
