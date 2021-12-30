#!/bin/bash

echo "fetching data"
./fetch_data.sh

echo "download imprint"
./dl_imprint.sh

echo "denormalize indices but exclude Schnitzler, Bahr and Wien"
denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@ref]/@ref" -x ".//tei:title[@level='a']/text()" -b pmb2121 -b pmb10815 -b pmb50

echo "create app"
ant