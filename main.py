import logging
import random

import psycopg2 as psycopg2
from aiogram import Bot, Dispatcher, executor, types
import spotipy
from spotipy import SpotifyClientCredentials
from config import API_TOKEN, CLIENT_ID, CLIENT_SECRET, PLAYLIST_ID, db_name, user_name, passwd, host, port

conn = psycopg2.connect(
    database=db_name, user=user_name, password=passwd, host=host, port=port
)


def startBot():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        dbConnect(2, message.chat.id, PLAYLIST_ID)
        print(f"{message.chat.username} prints: {message.text}")
        await message.answer("🌚")
        await message.answer("Привіт!")
        await message.answer("Ось список команд:")
        await message.answer("/start")
        await message.answer("/help")
        await message.answer("/getrandomsong")
        await message.answer("/setplaylist")

    @dp.message_handler(commands=['help'])
    async def help_funct(message: types.Message):
        print(f"{message.chat.username} prints: {message.text}")
        await message.answer("🌚")
        await message.answer("Ось список команд:")
        await message.answer("/help")
        await message.answer("/getrandomsong")
        await message.answer("/setplaylist")

    @dp.message_handler(commands=['getrandomsong'])
    async def getsong(message: types.Message):
        print(f"{message.chat.username} prints: {message.text}")
        songs = SpotifyActions(message.chat.id)
        random.seed()
        num = random.randint(0, len(songs) - 1)
        await message.answer(songs[num])

    @dp.message_handler(commands=['setplaylist'])
    async def setplaylist(message: types.Message):
        print(f"{message.chat.username} prints: {message.text}")
        if message.text.__contains__('/setplaylist https://open.spotify.com/playlist/'):
            dbConnect(3, message.chat.id, f'spotify:playlist:{message.text[47:69]}')
            await message.answer('Плейлист встановлено')
        else:
            await message.answer('Невірне посилання')
        # /setplaylist https://open.spotify.com/playlist/32VFNbn3sjpuD5iwlMz0CX?si=e38d45a9179347a1

    executor.start_polling(dp)


def SpotifyActions(user_id: int):
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    pl_id = dbConnect(1, user_id)
    if pl_id == '':
        pl_id = PLAYLIST_ID

    pl_res = sp.playlist(pl_id)
    msg = []
    for track in pl_res['tracks']['items']:
        msg.append(f"{track['track']['name']} - {track['track']['artists'][0]['name']} "
                   f"- {track['track']['external_urls']['spotify']}")
    return msg


def dbConnect(opcode: int = 0, user_id: int = 0, link: str = '') -> str:
    res = ''
    if link != '':
        link = f"'{link}'"
    cursor = conn.cursor()
    match opcode:
        case 1:
            if user_id != 0:
                cursor.execute(f'SELECT link FROM spotify1 WHERE id={user_id}')
                link = cursor.fetchone()
                res = link[0]
        case 2:
            if user_id != 0 and link != '':
                cursor.execute(f'INSERT INTO spotify1(id, link) VALUES({user_id}, {link})')
                conn.commit()
        case 3:
            if user_id != 0 and link != '':
                cursor.execute(f'UPDATE spotify1 Set link = {link} WHERE id={user_id}')
                conn.commit()
    cursor.close()
    return res


if __name__ == '__main__':
    startBot()

conn.close()
