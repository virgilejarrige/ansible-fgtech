# use case 3


## install ansible
```shell
 python3 -m venv venv
source venv/bin/activate
python -V
pip3 install ansible
python3 -m pip install --upgrade pip
ansible --version 
```
## latest ansible version from source
```shell
cd 
git clone https://github.com/ansible/ansible.git
git checkout tags/v2.19.1
git log --oneline
python3 -m venv ansible_latest
source ansible_latest/bin/activate
pip3 install -r requirements.txt
export PYTHONPATH=~/ansible/lib:$PYTHONPATH
export PATH=~/ansible/bin:$PATH
python -V
```