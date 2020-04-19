# Rubbergoddess

**This document needs updating before it is declared as master!**

![Rubbergoddess](https://repository-images.githubusercontent.com/238499660/ec829180-4868-11ea-948c-199e65da1347)

## About

This FEKTwide Discord bot manages the verification process, karma and some other
commands on VUT FEKT Discord server. [Rubbergod](https://github.com/Toaster192/rubbergod)'s younger sister.

## Installing and running the bot

Start by cloning the repo:
```
git clone https://github.com/sinus-x/rubbergoddess.git
cd rubbergoddess
```

### Option A: Docker compose setup

Install `docker` and `docker-compose` (use your package manager of choice) and 
run `docker` service (`systemctl start docker`).

_If neccesary, add the current user to the docker group with 
`sudo usermod -aG docker $USER`. You can verify this with `$ groups` (if there 
is a difference between `groups` and `groups $USER`, you need to restart your 
session)._

Build a docker container with `docker build .`.

To run the bot, run `docker-compose down && docker-compose up --build`, 
optionally with `--detach` parameter.

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

### First run
Use `config.template.py` file in `config` folder to set up Discord variables. 
See [USAGE.md]() if needed.

Aside from `config.py` file, you'll probably need to edit the `messages.py`, as 
well as some of the code, because roles and e-mails are hardcoded and server-specific. 
Just look through and keep editing until the bot runs as needed.

### Using the bot
Please note that the current state is not ready to be used on multiple servers. 

For example:
```python
    @commands.guild_only()
    @commands.group(aliases=["db"])
    @commands.has_any_role('MOD', 'SUBMOD')
    async def database (self, ctx: commands.Context):
```

This may seem safe, but anyone can create MOD role and read data from the 
database on their server.

## Authors

Rubbergoddess is mantained by [sinus-x](https://github.com/sinus-x) and [Czechbol](https://github.com/Czechbol).

Original authors include [Toaster](https://github.com/toaster192), 
[Matthew](https://github.com/matejsoroka), [Fpmk](https://github.com/TheGreatfpmK), 
[peter](https://github.com/peterdragun), [Urumasi](https://github.com/Urumasi) 
or [Leo](https://github.com/ondryaso).

## License

This project is licensed under the GNU GPL v.3 License.

Rubbergoddess image is a CC0 photography by Peter Sjo hosted on 
[unsplash.com](https://unsplash.com/photos/Nxy-6QwGMzA).
