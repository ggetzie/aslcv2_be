# 2024-05-21 Upgrading Python and Django.

We will update python to version 3.11 and Django to version 4.2

First install python 3.11

Reference [How to Install an Alternate Python Version](https://tiltingatwindmills.dev/how-to-install-an-alternate-python-version/)

## 1. Enable deb-src packages in the source lists.
```
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
sudo vim /etc/apt/sources.list
```
Uncomment all lines with `deb-src`. Use search and replace in vim: `:%s/^# deb-src/deb-src`

Save the file and update apt

```
sudo apt update
sudo apt upgrade
```

## 2. Install all build dependencies

```
sudo apt-get build-dep python3
sudo apt-get install build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev libmpdec-dev
```

## 3. Download the source tarball and unzip

```
cd ~/downloads
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xvvf Python-3.11.9.tgz
```

## 4. Build, Test, and then install the new Python version

```
cd ~/downloads/Python-3.11.9
./configure
make
make test
sudo make altinstall
```

Check that python3.11 is installed
```
$ python3.11 -V
Python 3.11.9
```

## 5. Delete the old venv and make a new one with Python3.11
The venv for aslcv2_be is stored in `/usr/local/src/env/aslcv2_be`. The code is installed at `/usr/local/src/aslcv2_be`.

Make sure all environment variables have been moved out of the venv activation script and saved in `/usr/local/src/aslcv2_be/.env`.
Compare the output of the following commands.

```
tail -n 20 /usr/local/src/env/aslcv2_be/bin/activate
cat /usr/local/src/aslcv2_be/.env
```
If all environment variables are correctly saved, go to the environment directory.

```
cd /usr/local/src/env
ls -l 
rm -r aslcv2_be
python3.11 -m venv aslcv2_be
```

## 6. Pull the latest version and install the updated requirements.txt in the new environment with pip
```
cd /usr/local/src/aslcv2_be
git pull origin master
source ../env/aslcv2_be/bin/activate
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
```

## 7. Run migrations, collectstatic and restart aslcv2_be services

```
cd /usr/local/src/aslcv2_be
source /usr/local/src/env/aslcv2_be/bin/activate
./manage.py migrate
./manage.py collectstatic --settings config.settings.production
./re_aslcv2_be
```






