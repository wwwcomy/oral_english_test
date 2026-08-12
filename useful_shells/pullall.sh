pwd
cd ~/github
current_path=`pwd`
echo $current_path
for file_a in `pwd`/*
do 
if [ -d $file_a ]
then
    echo "$file_a"
    cd "$file_a"
    git init
    git pull
fi
done