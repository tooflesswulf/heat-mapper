#!/bin/bash

folder="$1"
name="potato"

if [ ! -d $folder ]; then

mkdir $folder
cd $folder
mkdir dat
mkdir pkl
mkdir summary
cd summary
mkdir slices
cd ..

if [ ! -f potato.dat ]; then
cd dat
scp pi@192.168.86.180:~/heat-mapper/potato* .
mv potato.dat potato_final.dat
cd ..
scp pi@192.168.86.180:~/heat-mapper/layout.jpg .
touch potato.dat
cat dat/*.dat > potato.dat
fi

cd ..
source ~/tensorflow/bin/activate
python ~/heat-mapper2/data_processing/data_parser.py $1/potato.dat
deactivate

else
echo "$folder already exists."
fi
