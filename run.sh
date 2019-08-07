rm -r ./train/
rm -r ./test/
rm -r ./tmp
rm -r ./train_lmdb
rm -r ./test_lmdb
mkdir train
mkdir test
mkdir tmp
mkdir train_lmdb
mkdir test_lmdb
python ./split_data.py
python ./merge_train.py
rm -r ./train
mv ./tmp ./train
python ./create_dataset.py
