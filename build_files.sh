# Install Python if not installed
curl https://www.python.org/ftp/python/3.9.1/python-3.9.1.tgz -o python-3.9.1.tgz
tar -xvzf python-3.9.1.tgz
cd python-3.9.1
./configure
make
make install

# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
