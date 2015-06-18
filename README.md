Chulai Builder
==============

#Install
pyenv with python3.4.2+ is recommended

```bash
git clone git@github.com:chulai-la/builder.git
cd builder
pip install -r requirements.txt
cp config.cfg.sample config.cfg
vim config.cfg
```
you should set the right ssh-key for git as well
```
Host chulai
    HostName your.git.domain
    User git
    IdentityFile /path/to/your/deploy/key
```

View docs @ [chulai-doc](https://github.com/chulai-la/docs/blob/master/builder/api.md)
