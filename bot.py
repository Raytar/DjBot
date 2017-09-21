import discord
import asyncio
import json
import re
import youtube_dl


with open('config.json') as config_file:
    config = json.load(config_file)


client = discord.Client()
voice = None
player = None

def downoad_progress_hook(d):
    # Do something based on the download progress.
    if d["status"] == "finished":
        # do something useful probably
        pass

def download_audio(search):
    """Download audio based on the search
        Search can be an url or a youtube search
        File specifies the output file
    """

    url = search

    # download that shit!

    ydl_opts = {
        "outtmpl": "./audio_cache/%(id)s.%(ext)s",
        "restrict-filenames": True,
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        'progress_hooks': [downoad_progress_hook],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict.get("id", None)

@client.event
async def on_message(message):
    """Handle incoming messages:
        - Commands
            - %help             : Print help text
            - %play n, t        : play from url or title or song #n, set title to t
            - %resume           : resume audio
            - %pause            : pause audio
            - %stop             : stop audio and leave
            - %skip n           : skip n songs
            - %next             : next song
            - %prev             : load the previous song
            - %list             : show the playlist
            - %list remove n    : remove song #n
            - %list clear       : clear the playlist
        - Perform action
    """

    global client, voice, player

    cmd_prefix = "%"

    if (message.content.startswith(cmd_prefix)):
        command = re.match(r"%(\w+)\b", message.content)

        if command: 
            command = command.group(1)

        if not command:
            pass
        elif command == "help":
            # Send help info
            await client.send_message(message.channel, "Sorry, my programmer has not bothered to put anything here yet.")
        elif command == "play":
            url = re.search(r"https?://[^\s#]+", message.content).group(0);

            id = download_audio(url)

            # Start playing sweet tunes
            if not message.author.voice.is_afk and message.author.voice.voice_channel is not None:
                # Connect to voice
                if not voice:
                    voice = await client.join_voice_channel(message.author.voice.voice_channel)
                elif voice.channel != message.author.voice.voice_channel:
                    voice.move_to(message.author.voice.voice_channel)

                if player:
                    player.stop()

                player = voice.create_ffmpeg_player("./audio_cache/" + str(id) + ".mp3")
                player.start()

        elif command == "pause":
            if player and player.is_playing():
                player.pause()

        elif command == "resume":
            if player and not player.is_playing():
                player.resume()

        elif command == "stop":
            if player:
                player.stop()
        
        if player.error:
            print("Player error:" + str(player.error))


client.run(config["token"])
