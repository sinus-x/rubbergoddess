import json
import sys


class Config:
    def get(self, group: str, key: str):
        if group in self.c and key in self.c.get(group):
            v = self.c.get(group).get(key)
        elif key in self.d.get(group):
            v = self.d.get(group).get(key)
        else:
            v = None

        if v is not None:
            return v

        raise AttributeError(f'Configuration file: key "{key}" in "{group}" not found')

    def __init__(self):
        try:
            self.d = json.load(open("config/config.default.json", "r"))
            self.c = json.load(open("config/config.json", "r"))
        except FileNotFoundError:
            print("Error loading config files.")
            sys.exit(1)

        # fmt: off
        ##
        ## DATABASE
        self.db_states = self.get('database', 'states')
        self.db_string = self.get('database', 'string')

        ##
        ## BOT
        self.debug     = self.get('bot', 'debug')
        self.loader    = self.get('bot', 'loader')
        self.key       = self.get('bot', 'key')
        self.admin_id  = self.get('bot', 'admin id')
        self.guild_id  = self.get('bot', 'guild id')
        self.slave_id  = self.get('bot', 'slave guild id')
        self.host      = self.get('bot', 'host')
        self.prefixes  = self.get('bot', 'prefixes')
        self.prefix    = self.prefixes[0]

        self.extensions = self.get('bot', 'extensions')

        ##
        ## CHANNELS
        self.channel_jail     = self.get('channels', 'jail')
        self.channel_jailinfo = self.get('channels', 'jail-info')
        self.channel_mods     = self.get('channels', 'mods')
        self.channel_botdev   = self.get('channels', 'botdev')
        self.channel_botlog   = self.get('channels', 'botlog')
        self.channel_guildlog = self.get('channels', 'guildlog')
        self.channel_vote     = self.get('channels', 'vote')
        self.channel_botspam  = self.get('channels', 'botspam')
        self.channel_voices   = self.get('channels', 'voice group')
        self.channel_nomic    = self.get('channels', 'voice no mic')

        self.bot_allowed = self.get('channels', 'bot allowed')

        ##
        ## COLOR
        self.color         = self.get('color', 'main')
        self.color_success = self.get('color', 'success')
        self.color_notify  = self.get('color', 'notify')
        self.color_error   = self.get('color', 'error')
        self.colors = [self.color, self.color_success, self.color_notify, self.color_error]

        ##
        ## DELAY
        self.delay_embed  = self.get('delay', 'embed')
        self.delay_verify = self.get('delay', 'verify')

        ##
        ## EMAIL
        self.mail_address     = self.get('email', 'address')
        self.mail_smtp_server = self.get('email', 'server')
        self.mail_smtp_port   = self.get('email', 'port')
        self.mail_password    = self.get('email', 'password')

        ##
        ## ROLES
        self.role_verify    = self.get('roles', 'verify_id')
        self.role_mod       = self.get('roles', 'mod_id')
        self.roles_elevated = self.get('roles', 'elevated_ids')
        self.roles_native   = self.get('roles', 'native')
        self.roles_guest    = self.get('roles', 'guests')

        ##
        ## REACTION COG
        self.role_string   = self.get('reaction cog', 'trigger')
        self.role_channels = self.get('reaction cog', 'channels')
        self.pin_limit     = self.get('reaction cog', 'pin limit')

        ##
        ## KARMA COG
        self.karma_roles_ban    = self.get('karma cog', 'banned roles')
        self.karma_channels_ban = self.get('karma cog', 'banned channels')
        self.karma_string_ban   = self.get('karma cog', 'banned words')
        self.karma_subjects     = self.get('karma cog', 'count subjects')
        self.karma_vote_limit   = self.get('karma cog', 'vote limit')
        self.karma_vote_time    = self.get('karma cog', 'vote time')

        ##
        ## LIBRARIAN COG
        self.starting_week = self.get('librarian cog', 'starting week')
        self.nameday_cz    = self.get('librarian cog', 'nameday cz')
        self.nameday_sk    = self.get('librarian cog', 'nameday sk')
        self.weather_token = self.get('librarian cog', 'weather token')

        ##
        ## WARDEN COG
        self.rolehoarders = self.get('warden', 'rolehoarders')

        ##
        ## COMPATIBILITY
        self.noimitation = self.get('compatibility', 'ignored imitation channels')

        # fmt: on

    # fmt: off
    ##
    ## LONG LISTS
    ##
    subjects = [
        "aabs", "aana", "abce", "abch", "abej", "abin", "abse", "absn", "aeti",
        "afy1", "afy2", "afyz", "akme", "aldt", "ama1", "ama2", "ama3", "ambm",
        "amod", "amol", "aobf", "apbi", "apbt", "apfy", "aprg", "aprp", "arad",
        "aspe", "asta", "astd", "atpt", "auin", "aumi", "axbe", "azlp", "azsl",
        "azso", "bpc-ae1", "bpc-ae2", "bpc-aeb", "bpc-aei", "bpc-aey",
        "bpc-ah1", "bpc-ah2", "bpc-akr", "bpc-ald", "bpc-an4", "bpc-ana",
        "bpc-anh", "bpc-ant", "bpc-ars", "bpc-asi", "bpc-aud", "bpc-b2m",
        "bpc-b2t", "bpc-b2ta", "bpc-b2tb", "bpc-bap", "bpc-bca", "bpc-bcm",
        "bpc-bcs", "bpc-bct", "bpc-bcta", "bpc-bctb", "bpc-bps", "bpc-cpt",
        "bpc-crt", "bpc-czs", "bpc-dak", "bpc-dbs", "bpc-de1", "bpc-de2",
        "bpc-dee", "bpc-dhu", "bpc-dio", "bpc-diz", "bpc-dja", "bpc-dma",
        "bpc-dph", "bpc-dts", "bpc-eee", "bpc-ek1", "bpc-ek2", "bpc-el1",
        "bpc-el2", "bpc-ela", "bpc-elea", "bpc-elf", "bpc-elp", "bpc-els",
        "bpc-emc", "bpc-emv1", "bpc-emv2", "bpc-epb", "bpc-epr", "bpc-es2",
        "bpc-esb", "bpc-esi", "bpc-esm", "bpc-eso", "bpc-esop", "bpc-esos",
        "bpc-esot", "bpc-fy1", "bpc-fy1a", "bpc-fy1b", "bpc-fy2", "bpc-fy2b",
        "bpc-fys", "bpc-hel", "bpc-hnm", "bpc-ht1", "bpc-ht2", "bpc-hws",
        "bpc-i40", "bpc-ic1", "bpc-ic2", "bpc-int", "bpc-iot", "bpc-ise",
        "bpc-jez", "bpc-kez", "bpc-kkr", "bpc-kom", "bpc-kpn", "bpc-ks1",
        "bpc-ks2", "bpc-los", "bpc-ma1", "bpc-ma1b", "bpc-ma2", "bpc-ma3",
        "bpc-mam", "bpc-man", "bpc-mas", "bpc-mds", "bpc-mep", "bpc-mic",
        "bpc-mko", "bpc-mms", "bpc-mod", "bpc-mp2", "bpc-mpe", "bpc-mps",
        "bpc-mtp", "bpc-mts", "bpc-mva", "bpc-mvaa", "bpc-mve", "bpc-mvt",
        "bpc-nao", "bpc-ndi", "bpc-neo", "bpc-nez", "bpc-nkzt", "bpc-nrp",
        "bpc-nsp", "bpc-oko", "bpc-ook", "bpc-oop", "bpc-ozu", "bpc-pc1m",
        "bpc-pc1s", "bpc-pc1t", "bpc-pc2m", "bpc-pc2s", "bpc-pc2t", "bpc-pce",
        "bpc-pds", "bpc-pga", "bpc-pis", "bpc-pna", "bpc-pne", "bpc-pp1",
        "bpc-pp2", "bpc-ppa", "bpc-ppc", "bpc-ppk", "bpc-prm", "bpc-prp",
        "bpc-psd", "bpc-psm", "bpc-pst", "bpc-pts", "bpc-rbm", "bpc-reb",
        "bpc-rep", "bpc-res", "bpc-rjm", "bpc-rr1", "bpc-rr2", "bpc-rsk",
        "bpc-rzb", "bpc-sas", "bpc-sasb", "bpc-sbp", "bpc-scp", "bpc-sep",
        "bpc-si1", "bpc-si2", "bpc-sks", "bpc-sni", "bpc-sos", "bpc-sp1",
        "bpc-sp2", "bpc-spc", "bpc-spe", "bpc-spr", "bpc-ste", "bpc-stt",
        "bpc-sue", "bpc-sze", "bpc-szz", "bpc-tde", "bpc-tin", "bpc-tmb",
        "bpc-tmo", "bpc-trb", "bpc-tuz", "bpc-tvt", "bpc-udp", "bpc-uhb",
        "bpc-uhr", "bpc-uin", "bpc-uip", "bpc-ukb", "bpc-ume", "bpc-up1a",
        "bpc-up2a", "bpc-usk", "bpc-vee", "bpc-vel", "bpc-vft", "bpc-via",
        "bpc-vmp", "bpc-vs1", "bpc-vs2", "bpc-xup", "bpc-zda", "bpc-zes",
        "bpc-zha", "bpc-zin", "bpc-zkr", "bpc-zkz", "bpc-zsg", "bpc-zsw",
        "bpc-zsy", "bpc-zvs", "hac1", "hac2", "hana", "hars", "hbap", "hben",
        "hbts", "hcat", "hcpp", "hdan", "hdom", "hefe", "heit", "hele", "hesb",
        "heso", "heva", "hfyz", "hgrs", "hils", "hjdt", "hksy", "hma1", "hmpr",
        "hmtd", "hmva", "hodp", "hpa1", "hpa2", "hpa3", "hpa4", "hpa5", "hpa6",
        "hpop", "hpra", "hrre", "hsca", "hsep", "hsis", "htrs", "hvde",
        "xpc-ca1", "xpc-ca2", "xpc-ca3", "xpc-ca4", "xpc-ca5", "xpc-mw1",
        "xpc-mw2", "xpc-mw3", "xpc-mw4"
    ]
    # fmt: on


config = Config()
