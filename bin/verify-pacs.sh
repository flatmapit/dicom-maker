#!/bin/bash
# Verify PACS connection

set -e

if [ $# -ne 4 ]; then
    echo "Usage: $0 <host> <port> <aec> <aet>"
    echo ""
    echo "Arguments:"
    echo "  host  : PACS host address"
    echo "  port  : PACS port number"
    echo "  aec   : Application Entity Caller (your AE title)"
    echo "  aet   : Application Entity Title (PACS AE title)"
    echo ""
    echo "Example:"
    echo "  $0 localhost 4242 DICOM_MANAGER PACS1"
    exit 1
fi

HOST=$1
PORT=$2
AEC=$3
AET=$4

echo "🔍 Verifying PACS Connection"
echo "============================"
echo "Host: $HOST:$PORT"
echo "Calling AE: $AEC"
echo "Called AE: $AET"
echo ""

python3 -m dicom_maker.cli verify \
  --host "$HOST" \
  --port "$PORT" \
  --aec "$AEC" \
  --aet "$AET"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PACS connection verified successfully!"
else
    echo ""
    echo "❌ PACS connection verification failed"
    exit 1
fi
