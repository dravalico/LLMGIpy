# if on OSX you might need to install this stuff using eg homebrew
# brew install coreutils
# brew install curl

# download
curl https://archive.ics.uci.edu/ml/machine-learning-databases/00267/data_banknote_authentication.txt > Banknote.csv

# shuffle. use shuf instead of gshuf if on Linux
gshuf Banknote.csv | tr "," " " > Banknote_shuf.csv

# inspect
echo "Shuffled dataset"
wc Banknote_shuf.csv

# split into train/test
echo "#" > Banknote-Train.csv
head -n 1000 Banknote_shuf.csv >> Banknote-Train.csv
echo "#" > Banknote-Test.csv
tail -n 372 Banknote_shuf.csv >> Banknote-Test.csv

# inspect again
echo "Split datasets"
wc Banknote-T*.csv

echo "Original (start)"
head Banknote_shuf.csv
echo
echo "Train (start)"
head Banknote-Train.csv
echo
echo "Original (end)"
tail Banknote-Test.csv
echo
echo "Test (end)"
tail Banknote_shuf.csv
echo
