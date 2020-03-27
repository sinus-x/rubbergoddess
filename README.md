# Rubbergoddess

![Rubbergoddess](https://repository-images.githubusercontent.com/238499660/ec829180-4868-11ea-948c-199e65da1347)

## About

This FEKTwide Discord bot manages the verification process, karma and some other
commands on VUT FEKT Discord server. A [Rubbergod's](https://github.com/Toaster192/rubbergod) younger sister.

## Installing and running the bot

Prerequisites:
* Postgresql
* Python3.6+

Start by cloning the repo:
```
git clone https://github.com/sinus-x/rubbergoddess.git
cd rubbergoddess
```

### Option A: Docker compose setup

Install `docker` and `docker-compose` (use your package manager of choice) and run `docker` service (`systemctl start docker`).

_If neccesary, add the current user to the docker group with `sudo usermod -aG docker $USER`. You can
verify this with `$ groups` (if there is a difference between `groups` and `groups $USER`, you need
to restart your session)._

Build a docker container with `docker build .`.

To run the bot, run `docker-compose down && docker-compose up --build`, optionally with `--detach` parameter.

### Option B: Local setup

Install the required python modules (`venv` / `--user` flag recommended):
```
pip3 install -r requirements.txt
```

Run the bot (use `nohup` to run in detached mode) with `python3 rubbergoddess.py`.

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

## Authors

Rubbergoddess is mantained by [sinus-x](https://github.com/sinus-x).

Original authors include [Toaster](https://github.com/toaster192), [Matthew](https://github.com/matejsoroka), 
[Fpmk](https://github.com/TheGreatfpmK), [peter](https://github.com/peterdragun), [Urumasi](https://github.com/Urumasi) 
or [Leo](https://github.com/ondryaso).

## License

This project is licensed under the GNU GPL v.3 License.

Rubbergoddess image is a CC0 photography by Peter Sjo hosted on [unsplash.com](https://unsplash.com/photos/Nxy-6QwGMzA).
