from config.emotes import Emotes as emote

class Config:
    ##
    ## BASIC SETTINGS, NEEDED IN ORDER TO HAVE THE BOT RUN
    ##
    # Bot token. You have to create a bot on https://discordapp.com/developers.
    # Once your bot is created, you can generate your token on Bot tab.
    key = ''
    # This user will be mentioned when something goes wrong,
    # mostly by Verify cog.
    admin = 0
    # The ID of guild the bot is in
    guild = 0
    # Database connection link. You won't need to change this.
    db_string = "postgres://postgres:postgres@db:5432/postgres"
    # Prefixes the bot responds to.
    prefixes = ('?', '!')
    prefix = self.prefixes[0]
    # Extensions loaded on bot start.
    extensions = ['errors', 'base', 'karma', 'meme', 'random', 'verify',
                  'fitwide', 'review', 'vote', 'kachna', 'name_day',
                  'stalker', 'wormhole']
    # Channel IDs (used all over the code)
    channel_jail =    0 # Jail channel for verification
    channel_mods =    0 # Private channel, so database information does not leak outside
    channel_botdev =  0 # Bot development, where bot dumps its unhandled errors
    channel_log =     0 # Bot log, where important information is sent
    channel_vote =    0 # Channel for voting over emote's values
    channel_botspam = 0 # Channel for free bot spamming
    # Channels, where bot spamming won't trigger 'bot room redirect' message
    bot_allowed_channels = [
        channel_mods,
        channel_botspam,
        channel_botdev
    ]
    # Also see studets at the bottom of this file


    ##
    ## UTLITY VARIABLES
    ##
    # Settings for embeds.
    color =         0x54355F
    color_success = 0x1EBF49
    color_error =   0xD82B1C
    color_notify =  0xE58837
    delay_message = 2   # when to delete user's bot interacton, in seconds
    delay_embed =   120 # when to delete embed, in seconds
    delay_verify =  900 # when to delete verification messages, in seconds


    ##
    ## VERIFICATION COG
    ##
    # Verification email sender settings. See your e-mail inbox provider
    # for details.
    email_name = ''
    email_addr = ''
    email_smtp_server = ''
    email_smtp_port = 465
    email_pass = ''
    # Name of a role all verified users have
    verify = 'VERIFY'
    # Wich role are for local students and which are for guests.
    # Not used, at the time of wrinting this help.
    roles_native = ["FEKT"]
    roles_guest = ["VUT", "MUNI", "ČVUT", "CUNI", "VŠB", "GUEST"]


    ##
    ## KARMA COG
    ##
    # React-to-role trigger (how the message has to start).
    role_string = 'Role\n'
    # React-to-role trigger on channel-level base. No role string is needed.
    role_channels = [
        0, # add-programme
        0, # add-subjects
        0  # add-roles
    ]
    # Karma ban role. Usage unknown.
    karma_ban_role_id = -1
    # Channels where karma is not counted. Karma is only counted if reac-to-role
    # is not enabled for given post, so there is no need to blacklist #add-*
    # channels.
    karma_banned_channels = [
        0 # description
    ]
    # How long and how many votes a reaction has to have to set an emote value.
    vote_minimum = 5
    vote_minutes = 120
    # How many pin (📌) reaction post has to have to be automatically pinned.
    pin_count = 5


    ##
    ## RANDOM COG
    ##
    # Roll dice
    max_dice_at_once = 1000
    dice_before_collation = 20
    max_dice_groups = 10
    max_dice_sides = 10000


    ##
    ## KACHNA COG
    ## This cog is deprecated and has no real value. This is only the sign of 
    ## respect to the Rubbergod.
    ##
    # Where to link on ?kachna command
    kachna_link = '' # where to link on ?kachna command


    ##
    ## FITWIDE COG
    ##
    # How many users to print
    rolehoarder_limit = 10


    ##
    ## MEME COG
    ##
    # uh oh
    uhoh_string = 'uh oh'
    # Also see hugs on the bottom of the file


    ##
    ## NAME_DAY COG
    ##
    # name day source url
    name_day_url_cz = "http://svatky.adresa.info/json"
    name_day_url_sk = "http://svatky.adresa.info/json?lang=sk"


    ##
    ## WEATHER COG
    ##
    # Weather token to openweather API
    weather_token = "678a5932f6dd92ac668b20e9f89c0318"

    ##
    ## WORMHOLE COG
    ##
    wormhole_sibling = 0        # Sibling bot
    wormhole_target_channel = 0 # local wormhole channel
    wormhole_source_channel = 0 # source channel on shared server


    ##
    ## LONG LISTS
    ##
    # List of subjects the students can attend.
    # Used when generating links in #add-subjects, as well as disabling karma
    # (we had incidents of karma boosting in subject rooms, which resulted in
    # unfair advantage)
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
    # Hug emotes
    hug_emojis = [emote.hug_right, "(っ˘̩╭╮˘̩)っ", "(っ´▽｀)っ",
                  "╰(*´︶`*)╯", "(つ≧▽≦)つ", "(づ￣ ³￣)づ", "(づ｡◕‿‿◕｡)づ",
                  "(づ￣ ³￣)づ", "(っ˘̩╭╮˘̩)っ", "⁽₍੭ ՞̑◞ළ̫̉◟՞̑₎⁾੭",
                  "(੭ु｡╹▿╹｡)੭ु⁾⁾", "(*´σЗ`)σ", "(っ´▽｀)っ", "(っ´∀｀)っ",
                  "c⌒っ╹v╹ )っ", "(σ･з･)σ", "(੭ु´･ω･`)੭ु⁾⁾", "(oﾟ▽ﾟ)o",
                  "༼つ ் ▽ ் ༽つ", "༼つ . •́ _ʖ •̀ . ༽つ", "╏つ ͜ಠ ‸ ͜ಠ ╏つ",
                  "༼ つ ̥◕͙_̙◕͖ ͓༽つ", "༼ つ ◕o◕ ༽つ", "༼ つ ͡ ͡° ͜ ʖ ͡ ͡° ༽つ",
                  "(っಠ‿ಠ)っ", "༼ つ ◕_◕ ༽つ", "ʕっ•ᴥ•ʔっ", "", "༼ つ ▀̿_▀̿ ༽つ",
                  "ʕ ⊃･ ◡ ･ ʔ⊃", "╏つ” ⊡ 〜 ⊡ ” ╏つ", "(⊃｡•́‿•̀｡)⊃", "(っ⇀⑃↼)っ",
                  "(.づ◡﹏◡)づ.", "(.づσ▿σ)づ.", "(っ⇀`皿′↼)っ",
                  "(.づ▣ ͜ʖ▣)づ.", "(つ ͡° ͜ʖ ͡°)つ", "(⊃ • ʖ̫ • )⊃",
                  "（っ・∀・）っ", "(つ´∀｀)つ", "(っ*´∀｀*)っ", "(つ▀¯▀)つ",
                  "(つ◉益◉)つ", " ^_^ )>", "───==≡≡ΣΣ((( つºل͜º)つ",
                  "─=≡Σ((( つ◕ل͜◕)つ", "─=≡Σ((( つ ◕o◕ )つ",
                  "～～～～(/￣ｰ(･･｡)/", "───==≡≡ΣΣ(づ￣ ³￣)づ",
                  "─=≡Σʕっ•ᴥ•ʔっ", "───==≡≡ΣΣ(> ^_^ )>", "─=≡Σ༼ つ ▀̿_▀̿ ༽つ",
                  "───==≡≡ΣΣ(っ´▽｀)っ", "───==≡≡ΣΣ(っ´∀｀)っ", "～～(つˆДˆ)つﾉ>｡☆)ﾉ"]

