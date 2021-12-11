#!/bin/bash

MOTHER_PROD_DIR="/usr/share/pyshared/mother/machines/"
MOTHER_PREPRO_DIR="/root/mother/mother/machines/"
SCRIPT="machines_update.py"

# FUNC
function push() {
  case $1 in

      prod)
        echo "Copy script to mother prod"
        scp ./$SCRIPT root@mother.cent:$MOTHER_PROD_DIR/
        ;;
      prepro)
        echo "Copy script to mother prepro"
        scp ./$SCRIPT root@10.20.100.133:$MOTHER_PREPRO_DIR/
        ;;
      backup)
        echo "Copy PREPRO script from SERVER to locale dir."
        scp root@10.20.100.133:/root/mother/mother/machines/machines_update.py .
        ;;
      *)
        echo "Usage: $0 [prepro | prod | backup] # pomocnik pro kopirovani scriptu do motheru prepro / prod nebo ze serveru here"
        ;;
  esac
}

# MAIN
push $1  # copy local scripts to mother prod
