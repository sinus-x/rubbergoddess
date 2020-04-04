from config import config
from config.emotes import Emotes as emote

class Messages:
    prefix = config.Config.prefix

    server_warning = "Tohle funguje jen na VUT FEKT serveru."
    karma_get_missing = "Cauchy, musela jsem za tebe uklidit."
    missing_perms = "Na tohle nemáš prava. {user}"

    no_such_command = "Takový příkaz neznám. " + emote.sad
    spamming = "{user} Nespamuj tolik " + emote.sad
    insufficient_rights = "{user}, na použití tohoto příkazu nemáš právo."
    vote_room_only = "Tohle funguje jen v {room}."
    bot_room_redirect = "{user} " + emote.sad + " 👉 <#{bot_room}>\n"
    message_link_prefix = 'https://discordapp.com/channels/' + str(config.Config.guild_id) + '/'

    uhoh_counter = "{uhohs} uh ohs od spuštění."
    uptime_message = "Up since:  `{boottime}`\nUptime:\t`{uptime}`"

    kachna_grillbot = emote.wtf + " Tady kachna není, běž na FIT: " + config.Config.kachna_link
    
    rolehoarders_none = "Žádné jsem nenašla."

    karma = "{user} Karma uzivatele `{target}` je: **{karma}** " \
            "(**{order}.**)\nA rozdal:\n" \
            "**{karma_pos}** pozitivní karmy " \
            "(**{karma_pos_order}.**)\n" \
            "**{karma_neg}** negativní karmy " \
            "(**{karma_neg_order}.**)"

    karma_invalid_command = "Neznámý karma příkaz."
    karma_vote_format = "Neočekávám argument. " \
                        "Správný formát: `" + prefix + "karma vote`"
    karma_vote_message_hack = "Hlasování o karma ohodnocení emotu"
    karma_vote_message = karma_vote_message_hack + " {emote}"
    karma_vote_info = "Hlasování skončí za **{delay}** minut a minimální počet hlasů je **{minimum}**."
    karma_vote_result = "Výsledek hlasování o emotu {emote} je {result}."
    karma_vote_notpassed = "Hlasovani o emotu {emote} neprošlo\n" \
                           "Je potřeba alespoň {minimum} hlasů."
    karma_vote_allvoted = "Už se hlasovalo o všech emotech."
    karma_revote_format = "Očekávám pouze formát: `" + prefix + "karma revote [emote]`"
    karma_emote_not_found = "Emote jsem na serveru nenašla."
    karma_get_format = "Použití:\n" \
                       "`" + prefix + "karma get`: vypíše všechny emoty s hodnotou.\n" \
                       "`" + prefix + "karma get <emote>`: vrátí hodnotu daného emotu."
    karma_get = "Hodnota {emote} je {value}."
    karma_get_emote_not_voted = "{emote} není ohodnocen."
    karma_give_format = "Cauchy pls, formát je `" + prefix + "karma give [number] [user(s)]`"
    karma_give_format_number = "Cauchy pls, formát je `" + prefix + "karma give [number, ne {input}] [user(s)]` "
    karma_give_success = "Karma byla úspěšně přidaná."
    karma_give_negative_success = "Karma byla úspěšně odebraná."
    karma_message_format = prefix + "karma message [<url>|<id>]"
    member_not_found = "{user} Nikoho takového jsem nenašla."
    karma_lederboard_offser_error = "{user} Špatný offset, zadej kladné číslo"

    role_add_denied = "{user}, na přidání role {role} nemáš právo."
    role_remove_denied = "{user}, na odebrání role {role} nemáš právo."
    subject_add_denied_guest = "{user}, předměty si mohou přidávat jen studenti VUT."
    subject_remove_denied_guest = "{user}, předměty si mohou odebrat jen studenti VUT."
    subject_add_denied_notsubject = "{user}, přidávat se dají jen kanály předmětů."
    subject_remove_denied_notsubject = "{user}, odebrat se dají jen kanály předmětů."
    role_invalid_line = "{user}, řádek `{line}` je neplatný."
    role_format = "{user}, použij `" + prefix + "goddess`."
    role_not_on_server = "Nepíšeš na serveru, takže předpokládám, že myslíš role VUT FEKT serveru."
    role_not_role = "{user}, {not_role} není role."
    role_invalid_emote = "{user}, {not_emote} pro roli {role} není emote."

    rng_generator_format = "Použití: `" + prefix + "roll x [y]`\n" \
                           "x, y je rozmezí čísel,\n" \
                           "x, y jsou celá čísla,\n" \
                           "pokud y není specifikováno, je považováno za 0."
    rng_generator_format_number = "{user}, zadej dvě celá čísla, **integers**."

    rd_too_many_dice_in_group = "Příliš moc kostek v jedné skupině, maximum je {maximum}."
    rd_too_many_dice_sides = "Příliš moc stěn na kostkách, maximum je {maximum}."
    rd_too_many_dice_groups = "Příliš moc skupin kostek, maximum je {maximum}."
    rd_format = "Chybná syntax hodu ve skupině {group}."
    rd_help = "Formát naleznete na https://wiki.roll20.net/Dice_Reference\n" \
              "Implementovány featury podle obsahu: **8. Drop/Keep**"

    # VERIFY
    verify_no_email = "__Tvůj__ e-mail, {user} ({channel} {emote})"
    verify_login_only = "{user}, ještě chybí, jestli jsi přímo z FEKTu, nebo z VUT ({channel} {emote})"
    verify_no_login = "__Tvůj__ xlogin, {user} ({channel} {emote})"
    verify_wrong_arguments = "> ?verify **{login}**\n" + \
                             "{user}, podívej se do {channel} na příklad. {emote}"

    verify_already_sent = "{user}, e-mail už jsem ti jednou poslala (kdyžtak napiš DM {admin})"
    verify_already_verified_role = "{user}, tebe už znám... {admin}?"
    verify_already_verified_db = "{user} se podle záznamů už verifikoval... {admin}?"
    verify_send_kicked = "{admin}, {user} byl vykopnut a snaží se verifikovat."
    verify_send_banned = "{admin}, {user} byl zabanován a snaží se verifikovat."
    verify_send_success = "> {command}\n" + \
                          "V pořádku, {user}, poslala jsem ti ověřovací kód. " + \
                          "Pro verifikaci použij: `" + prefix + "submit kód`"
    verify_send_format = "Pro získání kódu použij příkaz podle toho, kam patříš:```\n" + \
                         "{}verify FEKT xlogin00\n".format(prefix) + \
                         "{}verify VUT xlogin00\n".format(prefix) + \
                         "{}verify e-mail (ideálně školní)```\n".format(prefix)

    verify_verify_no_code = "{user}, ten kód, který jsem ti poslala na e-mail {emote}"
    verify_verify_not_found = "{user}, nemám tě v databázi, je nutné zažádat o verifikační kód"
    verify_verify_wrong_code = "Špatný kód, {user}."
    verify_verify_manual = "{admin}, {user} asi nemá skupinu."
    verify_verify_success_private = "{user} Gratuluji k verifikaci!"
    verify_verify_success_public = emote.welcome + " Nový uživatel {user} byl úspěšně přidán s rolí **{group}**. "
    verify_congrats_fekt = "Obor si zapiš v <#692086702382121010>\n\n" \
                           "V <#692084608778633217> získáš další role pro zájmy\n" \
                           "Obecné informace jsou v <#692084651849678938>."
    verify_congrats_guest = "V <#692084608778633217> získáš role pro zájmy\n" \
                            "Obecné informace jsou v <#692084651849678938>."
    verify_verify_format = "{user}, pro verifikaci použij: `" + prefix + "submit kód`"

    verify_wrong_channel = "To zde použít nejde, {user}"

    # VOTE
    vote_format = "Použití vote:\n```" \
        + prefix + "vote [datum] [čas] [otázka]\n" \
        "<emote> <odpověď 1>\n" \
        "<emoji> <odpověď 2>\n" \
        "...```\n" \
        "Datum je ve formátu `dd.MM.(yy)`, čas `hh:mm`.\n" \
        "Pouze čas použije dnešní datum, pouze datum použije čas 00:00.\n" \
        "Bez argumentů času bude hlasování funkční neustále.\n" \
        "(Indikace výherné možnosti přežije i vypnutí.)"
    vote_not_emoji = "{not_emoji} není emoji. " + emote.sad
    vote_bad_date = "Hlasování může skončit jen v budoucnosti. " + emote.objection

    vote_winning = "Prozatím vyhrává možnost {winning_emoji} „{winning_option}“ s {votes} hlasy."
    vote_winning_multiple = "Prozatím vyhrávají možnosti {winning_emojis} s {votes} hlasy."

    vote_none = "Čekám na hlasy."

    vote_result = "V hlasování „{question}“ vyhrála možnost {winning_emoji} „{winning_option}“ s {votes} hlasy."
    vote_result_multiple = "V hlasování „{question}“ vyhrály možnosti {winning_emojis} s {votes} hlasy."
    vote_result_none = "V hlasování „{question}“ nikdo nehlasoval. " + emote.sad

    review_format = "```" + prefix + "reviews [add|remove|<zkratka předmětu>]```"
    review_add_format_short = "```" + prefix + "reviews add <zkratka> <známka 1-5> <Text recenze>```"
    review_add_format = review_add_format_short + \
                        "\nPříklad:\n" \
                        "```" + prefix +"reviews add bpc-kom 2 Text recenze```\n" \
                        "Pro vytvoření anonymní recenze zprávu pošlete do DM."

    review_wrong_subject = "Nesprávná zkratka předmětu"
    review_tier = "Číselné hodnocení je známka z rozsahu 1-5"
    review_text_len = "Maximální počet znaků je 1024"
    review_added = "Hodnocení předmětu bylo přidáno"
    reviews_page_e = "Pro aktualizaci zavolej reviews znovu"

    review_get_format = "```" + prefix + "reviews <zkratka předmětu>```"
    review_remove_format = "```" + prefix + "reviews remove <zkratka předmětu>```"
    review_remove_format_admin = "```" + prefix + "reviews remove <zkratka předmětu> [<id + číslo>]```"
    review_remove_id_format = "```reviews remove id <id>```"
    review_remove_success = "Hodnocení předmětu bylo odebráno"
    review_remove_error = "Hodnocení předmětu nebylo nalezeno"
    review_add_denied = "{user}, na přidání hodnocení předmětu nemáš právo."
    subject_format = "```" + prefix + "subject [add|remove] <zkratka předmětu>```"

    git_pr = "https://github.com/sinus-x/rubbergoddess/pulls"
    git_issues = "https://github.com/sinus-x/rubbergoddess/issues"
    uhoh = "uh oh"
    question = ["nech mě " + emote.sad, "nech mě " + emote.angry, emote.angry, emote.ree]
    
    name_day_cz = "Dnes má svátek {name} " + emote.happy
    name_day_sk = "Dnes má meniny {name} " + emote.happy

    info = [[('karma', 'Vypíše vaši karmu, kolik pozitivní a negativní karmy jste rozdali.'),
             ('karma stalk <user>', 'Vypíše karmu uživatele, kolik +/- karmy rozdal.'),
             ('karma get',
              'Vypíše, které emoty mají hodnotu 1 a -1.'),
             ('karma get <emote>',
              'Vrátí karma hodnotu emotu.'),
             ('karma vote',
              'Odstartuje hlasování o hodnotě zatím neohodnoceného emotu.'),
             ('karma revote <emote>',
              'Odstartuje hlasování o nové hodnotě emotu.'),
             ('karma message [<url>|<id>]',
              'Zobrazí karmu získanou za zprávu')],
            [('leaderboard [offset]', 'Karma leaderboard'),
             ('bajkarboard [offset]', 'Karma leaderboard v opačném pořadí'),
             ('givingboard [offset]', 'Leaderboard rozdávání pozitivní karmy.'),
             ('ishaboard [offset]', 'Leaderboard rozdávání negativní karmy.'),
             (review_add_format_short[4:].replace('`',''), 'Přidá recenzi na předmět.'),
             (review_get_format[4:].replace('`',''), 'Vypíše recenze na vybraný předmět.'),
             (review_remove_format[4:].replace('`',''), 'Odstraní hodnocení.'),
             ('vote', 'Zahájí hlasování.')],
            [('roll X Y',
              'Vygeneruje náhodné celé číslo z intervalu <**X**, **Y**>.'),
             ('flip', 'Hodí mincí'),
             ('pick *Is foo bar? Yes No Maybe*',
              'Vybere jedno ze slov za otazníkem.'),
             ('diceroll', 'Všechno možné házení kostkami.'),
             ('week', 'Vypíše, kolikátý je zrovna týden '
                      'a jestli je sudý nebo lichý.'),
             ('uhoh', 'Vypíše počet uh ohs od spuštění.'),
             ('uptime', 'Vypíše čas spuštění a čas uplynulý od spuštění.'),
             ('kachna', 'Nejsme FIT, ani to nezkoušej.'),
             ('goddess', 'Vypíše tuto zprávu.')]]

    # Core
    log_error = "Error in {channel} by {user}:\n> {command}"
    log_exception = "Exception in {channel} by {user}:\n> {command}\n{error}"

    # ERRORS
    exc_not_implemented = "To ještě neumím... " + emote.sad
    exc_no_permission = "Na to nemáš dostatečnou roli."
    exc_no_requirements = "Na to nemáš oprávnění."
    exc_no_command = "Takový příkaz neznám " + emote.sad
    exc_command_err = "Chyba v příkazu."
    exc_cooldown = "Tento příkaz nemůžeš zadávat tak často"
    exc_extension_err = "Chyba rozšíření " + emote.ree

    # VERIFY
    verify_not_jail = "Verifikovat se jde jen v #jail."

    # MEME
    meme_hug_not_found = "Nikoho takového nevidím " + emote.sad

    # STALKER
    stalker_err_not_found = "There are no users with specified parameters."
    stalker_err_read = "Could not read from database"
    stalker_err_new_entry_exists = "Given user ID is already present in the database"
    stalker_err_new_entry_write = "Could not write to the database"
    stalker_err_delete = "Could not delete user."
    stalker_err_delete_not_found = "User could not be deleted because is not in the database"
