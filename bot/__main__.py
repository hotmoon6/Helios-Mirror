from signal import signal, SIGINT
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from telegram.ext import CommandHandler
import random
from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, LOGGER, Interval, INCOMPLETE_TASK_NOTIFIER, DB_URI, alive, app, main_loop, AUTHORIZED_CHATS, app_session, USER_SESSION_STRING, \
    OWNER_ID, SUDO_USERS, START_BTN1_NAME, START_BTN1_URL, START_BTN2_NAME, START_BTN2_URL
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile, sendPhoto
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker

from .modules import authorize, list, cancel_mirror, mirror_status, mirror_leech, clone, ytdlp, shell, eval, delete, count, leech_settings, search, rss, bt_select, sleep
from .helper.ext_utils.telegraph_helper import telegraph

def progress_bar(percentage):
    p_used = '⬢'
    p_total = '⬡'
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage=int(percentage)
    except:
        percentage = 0
    return ''.join(
        p_used if i <= percentage // 10 else p_total for i in range(1, 11)
    )

def stats(update, context):
    if ospath.exists('.git'):
        last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'"], shell=True).decode()
    else:
        last_commit = 'No UPSTREAM_REPO'
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b><i><u>Bot Statistics</u></i></b>\n\n'\
            f'<b>CPU</b>:  {progress_bar(cpuUsage)} {cpuUsage}%\n' \
            f'<b>RAM</b>: {progress_bar(mem_p)} {mem_p}%\n' \
            f'<b>DISK</b>: {progress_bar(disk)} {disk}%\n\n' \
            f'<b>Updated:</b> {last_commit}\n'\
            f'<b>I am Working For:</b> <code>{currentTime}</code>\n\n'\
            f'<b>Total Disk:</b> <code>{total}</code> [{disk}% In use]\n'\
            f'<b>Used:</b> <code>{used}</code> | <b>Free:</b> <code>{free}</code>\n'\
            f'<b>T-UL:</b> <code>{sent}</code> | <b>T-DL:</b> <code>{recv}</code>\n'
    sendMessage(stats, context.bot, update.message)

def start(update, context):
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        Pic = ["https://graph.org/file/cbff456bdf713dbc94e77.jpg", "https://graph.org/file/49cf3d82dbf56af26deab.jpg", "https://graph.org/file/9e25a56f41522f8d1dcd6.jpg", "https://graph.org/file/2e179e25dc47dce3eb415.jpg", "https://graph.org/file/d171fa983d64db4e8345b.jpg", "https://graph.org/file/266fded681ee390e59d89.jpg"]
        start_string = f'''<b>My Name is Vecna ! An Pyrogram Based Mirror | Leech Telegram Bot to Upload Torrent or Direct Links to GDrive...</b>
<b>Tap /{BotCommands.HelpCommand} to get a list of available commands.</b>

<b>© Spidey | Mindflayer's Mirror</b>
'''
        unstart_string = f'''<b>It is an Official Bot of Mindflayer's Mirror. You can get Access only within the Group!</b>

<b>NOTE:</b> <code>All The Uploaded Links And Files Will Be Sent Here In Your Private Chat</code>'''
        sendPhoto(start_string, context.bot, update.message, random.choice(Pic))
    else:
        sendPhoto(unstart_string, context.bot, update.message, random.choice(Pic))

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    alive.kill()
    clean_all()
    srun(["pkill", "-9", "-f", "gunicorn|chrome|firefox|megasdkrest"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update.message)


help_string_telegraph = f'''
NOTE: Try each command without any perfix to see more detalis.<br><br>
<b>Mirror Related Commands:</b><br>
<b>/{BotCommands.MirrorCommand}</b> : Start mirroring to Google Drive.<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b>: Start mirroring and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b>: Start mirroring and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.QbMirrorCommand}</b>: Start Mirroring to Google Drive using qBittorrent.<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> : Start mirroring using qBittorrent and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b>: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.YtdlCommand}</b>: Mirror yt-dlp supported link.<br><br>
<b>/{BotCommands.YtdlZipCommand}</b>: Mirror yt-dlp supported link as zip.<br><br>
<b>Leech Related Commands:</b><br>
<b>/{BotCommands.LeechCommand}</b>: Start leeching to Telegram.<br><br>
<b>/{BotCommands.ZipLeechCommand}</b>: Start leeching and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b>: Start leeching and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.QbLeechCommand}</b>: Start leeching using qBittorrent.<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b>: Start leeching using qBittorrent and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b>: Start leeching using qBittorrent and upload the file/folder extracted from any archive extension<br><br>
<b>/{BotCommands.YtdlLeechCommand}</b>: Leech yt-dlp supported link.<br><br>
<b>/{BotCommands.YtdlZipLeechCommand}</b>: Leech yt-dlp supported link as zip.<br><br>
<b>Other Commands:</b><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive.<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive.<br><br>
<b>/{BotCommands.LeechSetCommand}</b> [query]: Leech settings.<br><br>
<b>/{BotCommands.SetThumbCommand}</b>: Reply photo to set it as Thumbnail.<br><br>
<b>/{BotCommands.BtSelectCommand}</b>: Select files from torrents by gid or reply.<br><br>
<b>/{BotCommands.CancelMirror}</b>: Cancel task by gid or reply.<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: Search in Google Drive(s).<br><br>
<b>/{BotCommands.SearchCommand}</b> [query]: Search for torrents with API.<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads.<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show stats of the machine where the bot is hosted in.<br><br>
<b>/{BotCommands.PingCommand}</b>: Check how long it takes to Ping the Bot (Only Owner & Sudo).<br><br>
<b>Sudo/Owner Only Commands:</b> <br>
<b>/{BotCommands.SleepCommand}:/</b> idle the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo).<br><br>
<b>/{BotCommands.CancelAllCommand}</b> [query]: Cancel all [status] tasks.<br><br>
<b>/{BotCommands.AuthorizeCommand}</b>: Authorize a chat or a user to use the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.UnAuthorizeCommand}</b>: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AuthorizedUsersCommand}</b>: Show authorized users (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AddleechlogCommand}</b>: Add Leech Log. (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RmleechlogCommand}</b>: Remove Leech Log. (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AddSudoCommand}</b>: Add sudo user (Only Owner).<br><br>
<b>/{BotCommands.RmSudoCommand}</b>: Remove sudo users (Only Owner).<br><br>
<b>/{BotCommands.RestartCommand}</b>: Restart and update the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.LogCommand}</b>: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).<br><br>
<b>/{BotCommands.ShellCommand}</b>: Run shell commands (Only Owner).<br><br>
<b>/{BotCommands.EvalCommand}</b>: Run Python Code Line | Lines (Only Owner).<br><br>
<b>/{BotCommands.ExecCommand}</b>: Run Commands In Exec (Only Owner).<br><br>
<b>/{BotCommands.ClearLocalsCommand}</b>: Clear <b>{BotCommands.EvalCommand}</b> or <b>{BotCommands.ExecCommand}</b> locals (Only Owner).<br><br>
<b>RSS Related Commands:</b><br>
<b>/{BotCommands.RssListCommand}</b>: List all subscribed rss feed info (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssGetCommand}</b>: Force fetch last N links (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssSubCommand}</b>: Subscribe new rss feed (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssUnSubCommand}</b>: Unubscribe rss feed by title (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssSettingsCommand}</b>[query]: Rss Settings (Only Owner & Sudo).<br><br>
'''
help_string = f'''
Basic Commands :-

<b>NOTE: After the Command Leave a single Space</b>

/mirror2: [url] Start mirroring to Google Drive.

<code>/mirror2 https://yoururl.com</code>

or (Reply with URL)

/qbmirror2: [magnet link] or Reply with Torrent - Start Mirroring to Google Drive using qBittorrent.

<code>/qbmirror2 magnet:?xt=urn:btih:f2cd08296a3...</code>

or (Reply with Torrent)

/clone2 [drive_url]: Copy Others file/folder to Google Drive.

<code>/clone2 https://drive.google.com/file/d/1e-fy8zXyz</code>

Complete Guide of Commands:-
'''
try:
    help = telegraph.create_page(
        title='Help from Vecna',
        content=help_string_telegraph,
    )["path"]
except Exception as err:
    LOGGER.warning(f"{err}")
    pass
def bot_help(update, context):
    button = ButtonMaker()
    button.buildbutton("Click Here", f"https://graph.org/{help}")
    reply_markup = button.build_menu(1)
    sendMarkup(help_string, context.bot, update.message, reply_markup)
def main():
    start_cleanup()
    notifier_dict = False
    if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
        if notifier_dict := DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = "Bot Restarted!"
                else:
                    msg = "Bot Restarted!"
                for tag, links in data.items():
                     msg += f"\n\n{tag}: "
                     for index, link in enumerate(links, start=1):
                         msg += f" <a href='{link}'>{index}</a> |"
                         if len(msg.encode()) > 4000:
                             if 'Restarted Successfully!' in msg and cid == chat_id:
                                 bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                                 osremove(".restartmsg")
                             else:
                                 try:
                                     bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                                 except Exception as e:
                                     LOGGER.error(e)
                             msg = ''
                if 'Restarted Successfully!' in msg and cid == chat_id:
                     bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                     osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Bot Restarted!", chat_id, msg_id)
        osremove(".restartmsg")
    elif not notifier_dict and AUTHORIZED_CHATS:
        for id_ in AUTHORIZED_CHATS:
            try:
                bot.sendMessage(id_, "Bot Restarted!", 'HTML')
            except Exception as e:
                LOGGER.error(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

app.start()
main()
if USER_SESSION_STRING:
    app_session.run()
else:
    pass
main_loop.run_forever()
