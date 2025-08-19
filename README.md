# YouTube Music Downloader

A Python-based tool for downloading and organizing audio content from YouTube with comprehensive metadata support and multiple audio format options.

<img width="1667" height="245" alt="image" src="https://github.com/user-attachments/assets/fc326e45-a832-4f28-8adf-4533375644df" />

## ⚠️ Important Legal Notice

This tool is intended for **educational purposes** and for downloading content that you have the legal right to download. Users are responsible for ensuring they comply with:

- YouTube's Terms of Service
- Copyright laws in their jurisdiction
- Fair use guidelines
- Content creator rights

**Please only download content that you own, have permission to download, or that falls under fair use in your jurisdiction.**

## Features

- **Multiple Audio Formats**: M4A (AAC), Opus, MP3 (various bitrates) - prioritizing YouTube's native formats
- **High-Quality Audio**: Native format preservation with best available quality
- **Smart Metadata Extraction**: Automatically parses artist, title, and album information
- **Thumbnail Embedding**: Downloads and embeds album artwork
- **Playlist Support**: Download entire playlists or individual videos
- **YouTube Music Integration**: Automatically converts YouTube Music URLs (works with Share button links from Public playlists)
- **Error Handling**: Robust error handling with retry mechanisms
- **Clean Output**: Organized file structure with proper metadata

## Requirements

- Python 3.7+
- FFmpeg (required for audio conversion)

### Python Dependencies

```bash
pip install yt-dlp mutagen pillow colorama
```

### FFmpeg Installation

**Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

**macOS**: 
```bash
brew install ffmpeg
```

**Linux**: 
```bash
sudo apt update && sudo apt install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ytmusic-downloader.git
cd ytmusic-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python music.py
```

## Usage

1. **Enter URL**: Paste a YouTube or YouTube Music video/playlist URL
   - For YouTube Music playlists: Use the "Share" button and ensure the playlist is set to **Public** visibility
   - Accepts both `music.youtube.com` and `youtube.com` URLs
   - Single videos and full playlists are supported
2. **Select Format**: Choose from 5 audio format options:
   - M4A (AAC) - YouTube's native format, best quality
   - Opus - YouTube's native format, efficient compression
   - MP3 320kbps - Universal compatibility, high quality
   - MP3 192kbps - Good quality, smaller files
   - MP3 128kbps - Basic quality, smallest files

3. **Automatic Processing**: The tool will:
   - Download audio in your selected format
   - Extract and embed metadata (title, artist, album)
   - Download and embed thumbnails as album art
   - Organize files in the `downloads` folder

## Supported Formats

| Format | Quality | File Size | Notes |
|--------|---------|-----------|-------|
| M4A (AAC) | Very High | Medium | YouTube's native format, no transcoding |
| Opus | Very High | Small | YouTube's native format, excellent compression |
| MP3 320kbps | Very High | Medium-Large | Universal compatibility |
| MP3 192kbps | High | Medium | Good balance of quality/size |
| MP3 128kbps | Good | Small | Smallest files, basic quality |

## Features in Detail

### Smart Metadata Parsing
- Automatically detects artist and song title from video titles
- Supports common separators: ` - `, ` – `, ` | `, `: `, ` by `
- Removes common suffixes like "(Official Video)" and "(Music Video)"
- Extracts additional metadata from video descriptions

### Thumbnail Processing
- Downloads the highest quality thumbnail available
- Converts WebP images to JPEG for better compatibility
- Embeds artwork directly into audio files
- Automatically cleans up temporary image files

### Error Recovery
- Continues downloading available tracks if some fail
- Processes existing files even if download errors occur
- Provides clear error messages and suggestions
- Skips unavailable or private videos gracefully

## File Organization

```
downloads/
├── Artist - Song Title.m4a
├── Artist - Another Song.opus
├── Artist - Third Song.mp3
└── ...
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

**"FFmpeg not found"**: Install FFmpeg and ensure it's in your system PATH

**"No audio streams found"**: The video may be region-locked or unavailable

**"Permission denied"**: Run with appropriate permissions or change output directory

**Slow downloads**: YouTube may be rate-limiting; try again later

### Getting Help

- Check that all dependencies are installed correctly
- Ensure FFmpeg is accessible from command line
- Verify the URL is valid and publicly accessible
- Try with a different video/playlist to isolate issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. The developers are not responsible for any misuse of this software. Users must ensure they have the legal right to download and use any content processed by this tool. Always respect content creators' rights and YouTube's Terms of Service.

---

**Note**: This tool downloads publicly available content from YouTube. It does not bypass any paywalls, DRM, or access private content. When using YouTube Music playlist links, ensure your playlists are set to Public visibility before sharing. Users are solely responsible for ensuring their use complies with applicable laws and terms of service.
