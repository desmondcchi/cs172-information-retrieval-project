# Runs flask server using indexed input
#!/bin/bash
# Usage:    ./flask.sh
#           sh flask.sh
#           bash flask.sh

export FLASK_APP=flask/flask_server
flask run -h 0.0.0.0 -p 8888