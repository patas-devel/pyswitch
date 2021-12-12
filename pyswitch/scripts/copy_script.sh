#!/bin/bash

MOTHER_PROD_DIR="/usr/share/pyshared/mother/machines/"
MOTHER_PREPRO_DIR="/root/mother/mother/machines/"
SCRIPT="machines_update.py"

# FUNC
function push() {
  case $1 in

      prod)
        echo "Copying script from DIR >>> SERVER MOTHER PROD"
        scp ./$SCRIPT root@mother.cent:$MOTHER_PROD_DIR/
        ;;
      prepro)
        echo "Copying script from DIR >>> SERVER MOTHER PREPRO"
        scp ./$SCRIPT root@10.20.100.133:$MOTHER_PREPRO_DIR/
        ;;
      backup)
        echo "Copying script from SERVER MOTHER PREPRO >>> to DIR"
        scp root@10.20.100.133:/root/mother/mother/machines/machines_update.py .
        ;;
      *)
        echo "Usage: $0 [prepro | prod | backup] # prod ... dir to server; prepro dir to server; backup ... server prepro to dir"
        ;;
  esac
}

# MAIN
push $1  # copy local scripts to mother prod
