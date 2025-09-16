#!/bin/bash
# Send a study to PACS

set -e

if [ $# -ne 5 ]; then
    echo "Usage: $0 <study-id> <host> <port> <aec> <aet>"
    echo ""
    echo "Arguments:"
    echo "  study-id  : DICOM Study Instance UID"
    echo "  host      : PACS host address"
    echo "  port      : PACS port number"
    echo "  aec       : Application Entity Caller (your AE title)"
    echo "  aet       : Application Entity Title (PACS AE title)"
    echo ""
    echo "Example:"
    echo "  $0 1.2.826.0.1.3680043.8.498.123456789 localhost 4242 DICOM_MANAGER PACS1"
    exit 1
fi

STUDY_ID=$1
HOST=$2
PORT=$3
AEC=$4
AET=$5

echo "📤 Sending Study to PACS"
echo "========================"
echo "Study ID: $STUDY_ID"
echo "Host: $HOST:$PORT"
echo "Calling AE: $AEC"
echo "Called AE: $AET"
echo ""

# First verify connection
echo "🔍 Verifying PACS connection..."
python3 -m dicom_maker.cli verify \
  --host "$HOST" \
  --port "$PORT" \
  --aec "$AEC" \
  --aet "$AET"

if [ $? -eq 0 ]; then
    echo ""
    echo "📤 Sending study to PACS..."
    python3 -m dicom_maker.cli send \
      --study-id "$STUDY_ID" \
      --host "$HOST" \
      --port "$PORT" \
      --aec "$AEC" \
      --aet "$AET"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Study sent successfully to PACS!"
    else
        echo ""
        echo "❌ Failed to send study to PACS"
        exit 1
    fi
else
    echo ""
    echo "❌ PACS connection verification failed"
    exit 1
fi
