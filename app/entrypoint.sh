#!/bin/bash
# entrypoint.sh

# Run the crud.py script
python3 crud.py

# Run the replicate_to_s3.py script
# python3 replicate_to_s3.py

# Keep the container running
tail -f /dev/null
