# Rubbergoddess

![Rubbergoddess](https://repository-images.githubusercontent.com/238499660/ec829180-4868-11ea-948c-199e65da1347)

## About

This FEKTwide Discord bot manages the verification process, karma and some other
commands on VUT FEKT Discord server. It is a younger sister of [Rubbergod](https://github.com/Toaster192/rubbergod).

## Installing and running the bot

Prerequisites:
* Postgresql
* Python3.6+

Start by cloning the repo:
```
git clone https://github.com/sinus-x/rubbergoddess.git
cd rubbergoddess
```

## Local setup (not recommended)

Install the required python modules (`venv` / `--user` flag recommended):
```
pip3 install -r requirements.txt
```

Run the bot (might want to use `nohup` or something):
```
python3 rubbergoddess.py
```

#### Required/recommended packages (apt)

```
git
python3.7
python3.7-dev
python3-pip
postgresql
postgresql-contrib
libpq-dev
```

## Docker compose setup

Install `docker` and `docker-compose` for your system (will vary from system to system)
and run `docker` (`systemctl start docker.service`)

If neccesray, add the current user to the docker group with `sudo usermod -aG docker $USER`.

```
docker build .
```

and then everytime you want to run the app

```
docker-compose down && docker-compose up --build
```

## Authors

Rubbergoddess is mantained by [sinus-x](https://github.com/sinus-x).

Original authors include [Toaster](https://github.com/toaster192), [Matthew](https://github.com/matejsoroka), [Fpmk](https://github.com/TheGreatfpmK), [peter](https://github.com/xdragu01), [Urumasi](https://github.com/Urumasi) or [Leo](https://github.com/ondryaso).

## License

This project is licensed under the GNU GPL v.3 License.

Rubbergoddess image is a CC0 photography by Peter Sjo hosted on [Unsplash.com](https://unsplash.com/photos/Nxy-6QwGMzA).