class Config:
    key = ''
    verification_role = ''
    admin_id = 663836659816857601 # for mention in case of false verification
    guild_id = 691291706116538429 # FEKT VUT

    # Verification email sender settings
    email_name = ''
    email_addr = ''
    email_smtp_server = 'smtp.gmail.com'
    email_smtp_port = 465
    email_pass = ''

    # Database
    db_string = "postgres://postgres:postgres@db:5432/postgres"

    # Base bot behavior
    command_prefix = ('?', '!')
    default_prefix = '?'

    # Extensions loaded on bot start
    extensions = ['base', 'karma', 'meme', 'random', 'verify', 'fitwide',
                  'acl', 'review', 'vote', 'kachna', 'name_day']

    # Roll dice
    max_dice_at_once = 1000
    dice_before_collation = 20
    max_dice_groups = 10
    max_dice_sides = 10000

    # Karma
    karma_ban_role_id = -1
    karma_banned_channels = [
        692086702382121010, # add-programme
        692626097669406720, # add-subjects
        692084608778633217  # add-roles
    ]

    # Voting
    vote_minimum = 20
    vote_minutes = 2

    # Pin emoji count to pin
    pin_count = 5

    # Special channel IDs
    log_channel = 692627997383065630     # bot-log
    bot_dev_channel = 692486570875551745 # bot-development
    vote_room = 692625063068827668       # bot-vote
    bot_room = 692484824769757265        # bot-spam
    mod_room = 691304580285202524        # mods

    allowed_channels = [
        bot_room,
        bot_dev_channel
    ]

    # String constants
    kachna_link = '' # where to link on ?kachna command

    role_string = 'Role\n'
    role_channels = [
        692086702382121010, # add-programme
        692626097669406720, # add-subjects
        692084608778633217  # add-roles
    ]
    hug_emojis = ["<:peepoHug:600435649786544151>",
                  "<:peepoHugger:602052621007585280>",
                  "<:huggers:602823825880514561>", "(っ˘̩╭╮˘̩)っ", "(っ´▽｀)っ",
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

    # Subjects shortcuts
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
    reviews_forbidden_roles = ["VUT", "MUNI", "GUEST"]

    # How many people to print if the limit argument is not specified
    rolehoarder_default_limit = 10

    # uh oh
    uhoh_string = 'uh oh'

    # grillbot
    grillbot_id = 0

    # kachna countdown
    kachna_open_hour = 16
    kachna_close_hour = 22
    kachna_open_days = [0, 2] # 0 = Monday, 1=Tuesday, 2=Wednesday...
    kachna_temp_closed = False

    # name day source url
    name_day_url_cz = "http://svatky.adresa.info/json"
    name_day_url_sk = "http://svatky.adresa.info/json?lang=sk"

    # weather token to openweather API
    weather_token = "678a5932f6dd92ac668b20e9f89c0318"
