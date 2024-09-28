name=${1::-4}
if test -e "$name-01.png"
then
	echo "skip conversion"
else
	echo "converting pdf to png ..."
	pdftoppm $1 $name -png -progress
fi

for i in `ls "$name-"*".png"`
do 
 	echo "$i" >> filelist.tmp
done

echo "run tesseract ..."
tesseract "filelist.tmp" "$name-ocr" -l lat pdf

rm filelist.tmp

rm "$name.pdf"

rm "$name-"*".png"
