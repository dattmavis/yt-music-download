import os
import yt_dlp
import sys
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, COMM
from PIL import Image
from colorama import Fore, Style, init
import re

init(autoreset=True)

def parse_artist_title(video_title):
    """Parse artist and title from video title using common patterns."""
    # Common separators for artist - title
    separators = [' - ', ' – ', ' — ', ' | ', ': ', ' by ']
    
    for sep in separators:
        if sep in video_title:
            parts = video_title.split(sep, 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                title = parts[1].strip()
                # Remove common suffixes
                for suffix in ['(Official Video)', '(Official Audio)', '(Lyric Video)', '(Music Video)', '[Official Video]', '[Official Audio]']:
                    title = title.replace(suffix, '').strip()
                return artist, title
    
    # If no separator found, assume the whole title is the song name
    clean_title = video_title
    for suffix in ['(Official Video)', '(Official Audio)', '(Lyric Video)', '(Music Video)', '[Official Video]', '[Official Audio]']:
        clean_title = clean_title.replace(suffix, '').strip()
    
    return None, clean_title

def extract_metadata(video_info):
    """Extract all available metadata from YouTube video info."""
    metadata = {}
    
    # Basic info
    title = video_info.get('title', '')
    uploader = video_info.get('uploader', video_info.get('channel', ''))
    description = video_info.get('description', '')
    upload_date = video_info.get('upload_date', '')
    
    # Parse artist and title from video title
    artist, song_title = parse_artist_title(title)
    
    # If we couldn't parse artist from title, use uploader as artist
    if not artist and uploader:
        artist = uploader
        song_title = title
    
    metadata['title'] = song_title or title
    metadata['artist'] = artist or uploader or 'Unknown Artist'
    metadata['album'] = video_info.get('album') or uploader or 'YouTube'
    metadata['date'] = upload_date[:4] if upload_date and len(upload_date) >= 4 else ''
    metadata['comment'] = f"Downloaded from: {video_info.get('webpage_url', '')}"
    
    # Try to extract more info from description
    if description:
        # Look for album info in description
        desc_lower = description.lower()
        if 'album:' in desc_lower:
            album_match = re.search(r'album:\s*([^\n]+)', description, re.IGNORECASE)
            if album_match:
                metadata['album'] = album_match.group(1).strip()
        
        # Look for genre
        if 'genre:' in desc_lower:
            genre_match = re.search(r'genre:\s*([^\n]+)', description, re.IGNORECASE)
            if genre_match:
                metadata['genre'] = genre_match.group(1).strip()
    
    return metadata

def embed_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata and thumbnail into audio file."""
    print(Fore.MAGENTA + f"Embedding metadata into {audio_path}..." + Style.RESET_ALL)
    
    if not os.path.exists(audio_path):
        print(Fore.RED + f"Audio file not found: {audio_path}" + Style.RESET_ALL)
        return
    
    try:
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        if file_ext == '.flac':
            embed_flac_metadata(audio_path, metadata, thumbnail_path)
        elif file_ext == '.mp3':
            embed_mp3_metadata(audio_path, metadata, thumbnail_path)
        elif file_ext in ['.ogg']:
            embed_ogg_metadata(audio_path, metadata, thumbnail_path)
        elif file_ext == '.opus':
            embed_opus_metadata(audio_path, metadata, thumbnail_path)
        elif file_ext in ['.m4a', '.mp4']:
            embed_mp4_metadata(audio_path, metadata, thumbnail_path)
        else:
            print(Fore.YELLOW + f"Unsupported format for metadata embedding: {file_ext}" + Style.RESET_ALL)
            
    except Exception as e:
        print(Fore.RED + f"Failed to embed metadata: {e}" + Style.RESET_ALL)

def embed_flac_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata into FLAC file."""
    audio = FLAC(audio_path)
    audio.clear()
    
    if metadata.get('title'):
        audio['TITLE'] = metadata['title']
    if metadata.get('artist'):
        audio['ARTIST'] = metadata['artist']
    if metadata.get('album'):
        audio['ALBUM'] = metadata['album']
    if metadata.get('date'):
        audio['DATE'] = metadata['date']
    if metadata.get('genre'):
        audio['GENRE'] = metadata['genre']
    if metadata.get('comment'):
        audio['COMMENT'] = metadata['comment']
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        with open(thumbnail_path, 'rb') as img:
            from mutagen.flac import Picture
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = 'image/jpeg'
            picture.desc = 'Cover'
            picture.data = img.read()
            audio.add_picture(picture)
    
    audio.save()
    print(Fore.GREEN + f"FLAC metadata embedded: {metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}" + Style.RESET_ALL)

def embed_mp3_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata into MP3 file."""
    audio = MP3(audio_path, ID3=ID3)
    
    if audio.tags is None:
        audio.add_tags()
    else:
        audio.tags.clear()
    
    if metadata.get('title'):
        audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    if metadata.get('artist'):
        audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
    if metadata.get('album'):
        audio.tags.add(TALB(encoding=3, text=metadata['album']))
    if metadata.get('date'):
        audio.tags.add(TDRC(encoding=3, text=metadata['date']))
    if metadata.get('comment'):
        audio.tags.add(COMM(encoding=3, lang='eng', desc='', text=metadata['comment']))
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        with open(thumbnail_path, 'rb') as img:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img.read()
            ))
    
    audio.save(v2_version=4)
    print(Fore.GREEN + f"MP3 metadata embedded: {metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}" + Style.RESET_ALL)

def embed_ogg_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata into OGG Vorbis file."""
    audio = OggVorbis(audio_path)
    
    if metadata.get('title'):
        audio['TITLE'] = metadata['title']
    if metadata.get('artist'):
        audio['ARTIST'] = metadata['artist']
    if metadata.get('album'):
        audio['ALBUM'] = metadata['album']
    if metadata.get('date'):
        audio['DATE'] = metadata['date']
    if metadata.get('genre'):
        audio['GENRE'] = metadata['genre']
    if metadata.get('comment'):
        audio['COMMENT'] = metadata['comment']
    
    audio.save()
    print(Fore.GREEN + f"OGG metadata embedded: {metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}" + Style.RESET_ALL)

def embed_opus_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata into Opus file."""
    from mutagen.oggopus import OggOpus
    audio = OggOpus(audio_path)
    
    if metadata.get('title'):
        audio['TITLE'] = metadata['title']
    if metadata.get('artist'):
        audio['ARTIST'] = metadata['artist']
    if metadata.get('album'):
        audio['ALBUM'] = metadata['album']
    if metadata.get('date'):
        audio['DATE'] = metadata['date']
    if metadata.get('genre'):
        audio['GENRE'] = metadata['genre']
    if metadata.get('comment'):
        audio['COMMENT'] = metadata['comment']
    
    audio.save()
    print(Fore.GREEN + f"Opus metadata embedded: {metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}" + Style.RESET_ALL)

def embed_mp4_metadata(audio_path, metadata, thumbnail_path=None):
    """Embeds metadata into MP4/M4A file."""
    audio = MP4(audio_path)
    
    if metadata.get('title'):
        audio['\xa9nam'] = [metadata['title']]
    if metadata.get('artist'):
        audio['\xa9ART'] = [metadata['artist']]
    if metadata.get('album'):
        audio['\xa9alb'] = [metadata['album']]
    if metadata.get('date'):
        audio['\xa9day'] = [metadata['date']]
    if metadata.get('genre'):
        audio['\xa9gen'] = [metadata['genre']]
    if metadata.get('comment'):
        audio['\xa9cmt'] = [metadata['comment']]
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        with open(thumbnail_path, 'rb') as img:
            from mutagen.mp4 import MP4Cover
            audio['covr'] = [MP4Cover(img.read(), MP4Cover.FORMAT_JPEG)]
    
    audio.save()
    print(Fore.GREEN + f"MP4 metadata embedded: {metadata.get('artist', 'Unknown')} - {metadata.get('title', 'Unknown')}" + Style.RESET_ALL)

def convert_youtube_music_url(youtube_url):
    """Converts YouTube Music playlist links to regular YouTube links."""
    if "music.youtube.com/playlist" in youtube_url:
        youtube_url = re.sub(r"music\.youtube\.com", "www.youtube.com", youtube_url)
        print(Fore.YELLOW + f"Converted YouTube Music link to: {youtube_url}" + Style.RESET_ALL)
    return youtube_url

def download_mp3(youtube_url, output_folder="downloads", format_choice="1"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    youtube_url = convert_youtube_music_url(youtube_url)

    # Configure audio format based on user choice
    format_configs = {
        "1": {"codec": "m4a", "quality": "0", "ext": "m4a"},
        "2": {"codec": "opus", "quality": "0", "ext": "opus"},
        "3": {"codec": "mp3", "quality": "320", "ext": "mp3"},
        "4": {"codec": "mp3", "quality": "192", "ext": "mp3"},
        "5": {"codec": "mp3", "quality": "128", "ext": "mp3"}
    }
    
    config = format_configs.get(format_choice, format_configs["1"])
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': config["codec"],
            'preferredquality': config["quality"],
        }],
        'writethumbnail': True,
        'outtmpl': os.path.join(output_folder, f'%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': False  
    }

    print(Fore.CYAN + "Starting download..." + Style.RESET_ALL)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=True)
        except yt_dlp.utils.DownloadError as e:
            print(Fore.RED + f"Error: {clean_error_message(str(e))}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Continuing with available downloads..." + Style.RESET_ALL)
            return process_existing_files(output_folder)

        if 'entries' in info:  # If it's a playlist
            for entry in info['entries']:
                if not entry or entry.get('url') is None:
                    print(Fore.YELLOW + f"Skipping unavailable video: {entry.get('title', 'Unknown Video')}" + Style.RESET_ALL)
                    continue
                
                title = entry.get('title', 'audio')
                audio_path = os.path.join(output_folder, f"{title}.{config['ext']}")
                thumbnail_path = find_thumbnail(output_folder, title)
                
                # Extract and embed metadata
                metadata = extract_metadata(entry)
                embed_metadata(audio_path, metadata, thumbnail_path)

            cleanup_thumbnails(output_folder)

        else:  # Single video case
            title = info.get('title', 'audio')
            audio_path = os.path.join(output_folder, f"{title}.{config['ext']}")
            thumbnail_path = find_thumbnail(output_folder, title)
            
            # Extract and embed metadata
            metadata = extract_metadata(info)
            embed_metadata(audio_path, metadata, thumbnail_path)
            cleanup_thumbnails(output_folder)

    print(Fore.GREEN + "Download complete!" + Style.RESET_ALL)

def clean_error_message(error_text):
    """Extracts a readable error message from yt-dlp's output."""
    if "Private video" in error_text:
        return "This video is private. Sign in to access it."
    if "Video unavailable" in error_text:
        return "This video is unavailable."
    if "Incomplete data received" in error_text:
        return "YouTube did not provide complete data. Retrying failed."
    return error_text.split('\n')[0]  

def process_existing_files(output_folder):
    """If errors occur, still embed album covers and basic metadata in already downloaded audio files."""
    print(Fore.YELLOW + "Processing existing audio files and thumbnails..." + Style.RESET_ALL)

    for file in os.listdir(output_folder):
        if file.endswith((".flac", ".mp3", ".ogg", ".opus", ".m4a", ".mp4")):
            title = os.path.splitext(file)[0]
            audio_path = os.path.join(output_folder, file)
            thumbnail_path = find_thumbnail(output_folder, title)

            # Create basic metadata from filename
            artist, song_title = parse_artist_title(title)
            metadata = {
                'title': song_title or title,
                'artist': artist or 'Unknown Artist',
                'album': 'YouTube',
                'comment': 'Downloaded from YouTube'
            }
            
            embed_metadata(audio_path, metadata, thumbnail_path)

    cleanup_thumbnails(output_folder)
    print(Fore.GREEN + "Processing complete!" + Style.RESET_ALL)

def find_thumbnail(output_folder, title):
    """Finds the correct thumbnail for each audio file."""
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        path = os.path.join(output_folder, f"{title}.{ext}")
        if os.path.exists(path):
            if ext == 'webp':  
                converted_path = path.replace('.webp', '.jpg')
                Image.open(path).convert("RGB").save(converted_path, "JPEG")
                return converted_path
            return path
    return None  # If no image is found


def cleanup_thumbnails(output_folder):
    """Deletes all remaining thumbnail images."""
    deleted_anything = False
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        for file in os.listdir(output_folder):
            if file.endswith(f".{ext}"):
                path = os.path.join(output_folder, file)
                os.remove(path)
                deleted_anything = True
                print(Fore.RED + f"Deleted: {path}" + Style.RESET_ALL)

    if not deleted_anything:
        print(Fore.YELLOW + "No leftover thumbnails found to delete." + Style.RESET_ALL)

if __name__ == "__main__":
    url = input(Fore.BLUE + "Enter YouTube video or playlist URL: " + Style.RESET_ALL)
    
    print(Fore.CYAN + "\nSelect audio format:" + Style.RESET_ALL)
    print(Fore.WHITE + "1. M4A (AAC) - YouTube's native format, best quality")
    print("2. Opus - YouTube's native format, efficient compression")
    print("3. MP3 (320kbps) - Universal compatibility")
    print("4. MP3 (192kbps) - Good quality, smaller files")
    print("5. MP3 (128kbps) - Basic quality, smallest files" + Style.RESET_ALL)
    
    format_choice = input(Fore.BLUE + "Enter your choice (1-5): " + Style.RESET_ALL).strip()
    
    download_mp3(url, format_choice=format_choice)
