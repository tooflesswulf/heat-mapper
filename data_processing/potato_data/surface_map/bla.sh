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
ssh pi@192.168.86.180 'raspistill -o layout.jpg'
scp pi@192.168.86.180:~/layout.jpg .
touch potato.dat
cat dat/*.dat > potato.dat
else
echo "Not pulling files from pi because they already exist."
fi

cd ..

else
echo "$folder already exists."
fi

source ~/tensorflow/bin/activate
python ~/heat-mapper2/data_processing/data_parser.py $folder/potato.dat
#python ~/heat-mapper2/data_processing/visualize_short.py $folder/summary/
deactivate
