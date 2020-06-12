from core.config import config
from core.emote import emote


class Messages:
    prefix = config.prefix

    server_warning = "Tohle funguje jen na VUT FEKT serveru."
    karma_get_missing = "Cauchy, musela jsem za tebe uklidit."
    missing_perms = "Na tohle nemáš prava. {user}"

    no_such_command = "Takový příkaz neznám. " + emote.sad
    spamming = "{user} Nespamuj tolik " + emote.sad
    insufficient_rights = "{user}, na použití tohoto příkazu nemáš právo."
    vote_room_only = "Tohle funguje jen v {room}."
    bot_room_redirect = "{user} " + emote.sad + " 👉 <#{bot_room}>\n"
    message_link_prefix = "https://discordapp.com/channels/" + str(config.guild_id) + "/"

    karma = (
        "{user} Karma uživatele `{target}` je **{karma}** "
        "(**{order}.**)\nA rozdal:\n"
        "**{karma_pos}** pozitivní karmy "
        "(**{karma_pos_order}.**)\n"
        "**{karma_neg}** negativní karmy "
        "(**{karma_neg_order}.**)"
    )

    karma_invalid_command = "Neznámý karma příkaz."
    karma_vote_format = "Neočekávám argument. " "Správný formát: `" + prefix + "karma vote`"
    karma_vote_message_hack = "Hlasování o karma ohodnocení emotu"
    karma_vote_message = karma_vote_message_hack + " {emote}"
    karma_vote_info = (
        "Hlasování skončí za **{delay}** minut a minimální počet hlasů je **{minimum}**."
    )
    karma_vote_result = "Výsledek hlasování o emotu {emote} je {result}."
    karma_vote_notpassed = (
        "Hlasovani o emotu {emote} neprošlo\n" "Je potřeba alespoň {minimum} hlasů."
    )
    karma_vote_allvoted = "Už se hlasovalo o všech emotech."
    karma_revote_format = "Očekávám pouze formát: `" + prefix + "karma revote [emote]`"
    karma_emote_not_found = "Emote jsem na serveru nenašla."
    karma_get_format = (
        "Použití:\n"
        "`" + prefix + "karma get`: vypíše všechny emoty s hodnotou.\n"
        "`" + prefix + "karma get <emote>`: vrátí hodnotu daného emotu."
    )
    karma_get = "Hodnota {emote} je {value}."
    karma_get_emote_not_voted = "{emote} není ohodnocen."
    karma_give_format = "Cauchy pls, formát je `" + prefix + "karma give [number] [user(s)]`"
    karma_give_format_number = (
        "Cauchy pls, formát je `" + prefix + "karma give [number, ne {input}] [user(s)]` "
    )
    karma_give_success = "Karma byla úspěšně přidaná."
    karma_give_negative_success = "Karma byla úspěšně odebraná."
    karma_message_format = prefix + "karma message [<url>|<id>]"
    member_not_found = "{user} Nikoho takového jsem nenašla."
    karma_lederboard_offser_error = "{user} Špatný offset, zadej kladné číslo"

    rng_generator_format = (
        "Použití: `" + prefix + "roll x [y]`\n"
        "x, y je rozmezí čísel,\n"
        "x, y jsou celá čísla,\n"
        "pokud y není specifikováno, je považováno za 0."
    )
    rng_generator_format_number = "{user}, zadej dvě celá čísla, **integers**."

    review_format = "```" + prefix + "reviews [add|remove|<zkratka předmětu>]```"
    review_add_format_short = (
        "```" + prefix + "reviews add <zkratka> <známka 1-5> <Text recenze>```"
    )
    review_add_format = (
        review_add_format_short + "\nPříklad:\n"
        "```" + prefix + "reviews add bpc-kom 2 Text recenze```\n"
        "Pro vytvoření anonymní recenze zprávu pošlete do DM."
    )

    review_wrong_subject = "Nesprávná zkratka předmětu"
    review_tier = "Číselné hodnocení je známka z rozsahu 1-5"
    review_text_len = "Maximální počet znaků je 1024"
    review_added = "Hodnocení předmětu bylo přidáno"
    reviews_page_e = "Pro aktualizaci zavolej reviews znovu"

    review_get_format = "```" + prefix + "reviews <zkratka předmětu>```"
    review_remove_format = "```" + prefix + "reviews remove <zkratka předmětu>```"
    review_remove_format_admin = (
        "```" + prefix + "reviews remove <zkratka předmětu> [<id + číslo>]```"
    )
    review_remove_id_format = "```reviews remove id <id>```"
    review_remove_success = "Hodnocení předmětu bylo odebráno"
    review_remove_error = "Hodnocení předmětu nebylo nalezeno"
    review_add_denied = "{user}, na přidání hodnocení předmětu nemáš právo."
    subject_format = "```" + prefix + "subject [add|remove] <zkratka předmětu>```"

    info = [
        [
            ("karma", "Vypíše vaši karmu, kolik pozitivní a negativní karmy jste rozdali."),
            ("karma stalk <user>", "Vypíše karmu uživatele, kolik +/- karmy rozdal."),
            ("karma get", "Vypíše, které emoty mají hodnotu 1 a -1."),
            ("karma get <emote>", "Vrátí karma hodnotu emotu."),
            ("karma vote", "Odstartuje hlasování o hodnotě zatím neohodnoceného emotu."),
            ("karma revote <emote>", "Odstartuje hlasování o nové hodnotě emotu."),
            ("karma message [<url>|<id>]", "Zobrazí karmu získanou za zprávu"),
        ],
        [
            ("leaderboard [offset]", "Karma leaderboard"),
            ("bajkarboard [offset]", "Karma leaderboard v opačném pořadí"),
            ("givingboard [offset]", "Leaderboard rozdávání pozitivní karmy."),
            ("ishaboard [offset]", "Leaderboard rozdávání negativní karmy."),
            (review_add_format_short[4:].replace("`", ""), "Přidá recenzi na předmět."),
            (review_get_format[4:].replace("`", ""), "Vypíše recenze na vybraný předmět."),
            (review_remove_format[4:].replace("`", ""), "Odstraní hodnocení."),
            ("vote", "Zahájí hlasování."),
        ],
        [
            ("roll X Y", "Vygeneruje náhodné celé číslo z intervalu <**X**, **Y**>."),
            ("flip", "Hodí mincí"),
            ("pick *Is foo bar? Yes No Maybe*", "Vybere jedno ze slov za otazníkem."),
            ("diceroll", "Všechno možné házení kostkami."),
            ("week", "Vypíše, kolikátý je zrovna týden " "a jestli je sudý nebo lichý."),
            ("uhoh", "Vypíše počet uh ohs od spuštění."),
            ("uptime", "Vypíše čas spuštění a čas uplynulý od spuštění."),
            ("kachna", "Nejsme FIT, ani to nezkoušej."),
            ("goddess", "Vypíše tuto zprávu."),
        ],
    ]

    # Core
    log_error = "Error in {channel} by {user}:\n> {command}"
    log_exception = "Exception in {channel} by {user}:\n> {command}\n{error}"
    db_update_successful = "V pořádku {user}, změnu jsem si uložila."

    # ERRORS
    err_not_implemented = "To ještě neumím... " + emote.sad
    err_not_supported = "To nejde."
    err_no_permission = "Na to nemáš dostatečnou roli."
    err_no_permission_bot = "Na to nemám oprávnění."
    err_no_requirements = "Nesplnili jste podmínky příkazu."
    err_no_command = "Takový příkaz neznám " + emote.sad
    err_command_err = "Chyba v příkazu."
    err_cooldown = "Tento příkaz nemůžeš zadávat tak často"
    err_extension_err = "Chyba rozšíření " + emote.ree
    err_bad_argument = "Chyba v parsování argumentu " + emote.sad
