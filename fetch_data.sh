# bin/bash

rm master.zip
rm -rf ./Hermann-Bahr_Arthur-Schnitzler-master
rm -rf data
wget https://github.com/acdh-oeaw/Hermann-Bahr_Arthur-Schnitzler/archive/refs/heads/master.zip
unzip master
ant -f copy-task.xml
rm master.zip
./dl_imprint.sh

echo "add # to @refs"
find ./data/editions/ -type f -name "*.xml"  -print0 | xargs -0 sed -i -e 's@ref="pmb@ref="#pmb@g'

echo "denormalize indices "
denormalize-indices -f "./data/*/*.xml" -i "./data/indices/*.xml" -m ".//*[@ref]/@ref" -x ".//tei:title[@level='a']/text()" -b pmb2121 -b pmb10815 -b pmb50

echo "build typesense index"
python make_typesense_index.py