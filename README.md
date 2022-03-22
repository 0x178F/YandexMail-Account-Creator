## Installation
```sh
git clone https://github.com/0x178F/YandexMail-Account-Creator
```

## Requirements
```sh
Python 3.6+
```
```sh
pip install -r requirements.txt
```

## Usage
```sh
python main.py
```

## Configuration
Edit the settings.json file.

|Config|Usage|
| :------------: | :------------: |
|api_key|2Captcha API key you will use to solve captcha|
|secret_question|secret question to be created when registering|
|secret_answer|secret answer to be created when registering|

If you have a first and last name list, you can add it to the firstname.txt and lastname.txt files in the data folder.

If you want to use a proxy, you can add it to the proxylist.txt file in the data folder.
```sh
Proxy Format: ip:port or user:pass@10.10.1.10:3128
```

## Features
- Proxy Support.
- Adb Support.
- Multi-Thread.
- Enabling optional imap when creating an account.
- Auto generates all information except name and surname.

## Screenshot
![YandexMail-Creator-Bot](https://github.com/0x178F/YandexMail-Account-Creator/blob/master/img/YandexCreator.gif?raw=true "YandexMail-Creator-Bot")