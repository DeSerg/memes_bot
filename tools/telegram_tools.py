import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import extern as ext

import modules.db as db


FormatCounter = ' {}'
FormatLikes = '😂{}'
FormatNeutrals = '🤨{}'
FormatDislikes = '😡{}'


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def build_reply_markup(likes=0, neutrals=0, dislikes=0):
    likes_text = ''
    neutrals_text = ''
    dislikes_text = ''

    if likes >= 0:
        likes_text = FormatCounter.format(likes)

    if neutrals >= 0:
        neutrals_text = FormatCounter.format(neutrals)

    if dislikes >= 0:
        dislikes_text = FormatCounter.format(dislikes)

    button_list = [
        InlineKeyboardButton(FormatLikes.format(likes_text), callback_data=db.TableNameLikes),
        InlineKeyboardButton(FormatNeutrals.format(neutrals_text), callback_data=db.TableNameNeutrals),
        InlineKeyboardButton(FormatDislikes.format(dislikes_text), callback_data=db.TableNameDislikes)
    ]

    return InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

