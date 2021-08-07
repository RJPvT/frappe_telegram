from typing import Union
from telegram.ext import Updater


import frappe
from frappe_telegram.frappe_telegram.doctype import TelegramBot


def start_polling(site: str, telegram_bot: Union[str, TelegramBot], poll_interval: int = 0):
    updater = get_bot(telegram_bot=telegram_bot, site=site)

    updater.start_polling(poll_interval=poll_interval)
    updater.idle()


def start_webhook(
        site: str,
        telegram_bot: Union[str, TelegramBot],
        listen_host: str = "127.0.0.1",
        webhook_port: int = 80,
        webhook_url: str = None):
    updater = get_bot(telegram_bot=telegram_bot, site=site)
    updater.start_webhook(
        listen=listen_host,
        port=webhook_port,
        webhook_url=webhook_url
    )


def get_bot(telegram_bot: Union[str, TelegramBot], site=None) -> Updater:
    if not site:
        site = frappe.local.site

    from contextlib import ExitStack
    with frappe.init_site(site) if not frappe.db else ExitStack():
        if not frappe.db:
            frappe.connect()

        if isinstance(telegram_bot, str):
            telegram_bot = frappe.get_doc("Telegram Bot", telegram_bot)

        token = telegram_bot.get_password("api_token")

        updater = Updater(token=token)
        handlers = frappe.get_hooks("telegram_bot_handler")
        if isinstance(handlers, dict):
            handlers = handlers[telegram_bot.name]

        for cmd in handlers:
            frappe.get_attr(cmd)(botname=telegram_bot.name, updater=updater)

    return updater
