# 🎧 Moodle to MP3 Converter

Convert Moodle lecture videos to MP3 files for NotebookLM transcription.

## 🎯 Project Purpose

This project serves as a **learning playground** for:
- **Git Branching** - Practice with feature branches, merging, and branch workflows
- **CI/CD Basics** - Understanding pipelines and GitHub Actions triggers
- **Collaboration** - Pull requests, code reviews, and branch protection

## Quick Start

### Step 1: Extract Video Links (in Browser)

1. Open your Moodle course page with the video table
2. Press `F12` to open DevTools → Console tab
3. Paste and run this code:

```javascript
(async () => {
    const tableBody = document.querySelector("#videoslist_table > tbody");
    if (!tableBody) { alert("Table not found!"); return; }
    
    const links = Array.from(tableBody.querySelectorAll("a"))
        .map(a => a.href)
        .filter(href => href.includes("php") || href.includes("video"));
    
    console.log(`Found ${links.length} sub-pages. Fetching videos...`);
    
    let videos = [];
    for (let i = 0; i < links.length; i++) {
        console.log(`Processing ${i+1}/${links.length}...`);
        try {
            const html = await fetch(links[i]).then(r => r.text());
            const match = html.match(/https?:\/\/[^"'\s]+\.mp4/i);
            if (match) videos.push(match[0]);
        } catch(e) { console.error(e); }
    }
    
    const unique = [...new Set(videos)];
    copy(unique.join('\n'));
    console.log(`✅ ${unique.length} video URLs copied to clipboard!`);
    alert(`${unique.length} links copied! Paste into links.txt`);
})();
```

4. Links are now in your clipboard!

### Step 2: Download & Convert

1. Open `links.txt` and paste the links (replace the placeholder)
2. **Close Chrome completely** (required for cookie access)
3. Double-click `RUN_ME.bat`
4. Wait for downloads to complete
5. Find your MP3 files in the `mp3_output` folder!

## Requirements

- Python 3.x
- Chrome or Edge browser
- FFmpeg (for MP3 conversion)

### Install FFmpeg

Download from https://ffmpeg.org/download.html and add to PATH, or:

```powershell
# With Chocolatey
choco install ffmpeg

# With Winget
winget install FFmpeg
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Access denied" | Close Chrome, then run again |
| "FFmpeg not found" | Install FFmpeg and add to PATH |
| Using Edge? | Edit `download_and_convert.py`, change `chrome` to `edge` |
| Partial downloads | Some links may be broken, check console output |

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest test_download_and_convert.py -v

# Run with coverage
pytest test_download_and_convert.py -v --cov=download_and_convert
```

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration:
- Runs tests on every push and pull request
- Tests against Python 3.9, 3.10, 3.11, and 3.12
- Generates coverage reports

Check the [Actions tab](../../actions) to see the pipeline status.

## 📁 Project Structure

```
moodle-to-audio/
├── .github/
│   └── workflows/
│       └── tests.yml          # CI/CD pipeline
├── download_and_convert.py    # Main script
├── test_download_and_convert.py  # Unit tests
├── links.txt                  # Input file for video links
├── moodle_video_extractor.user.js  # Browser userscript
├── RUN_ME.bat                 # Windows launcher
└── README.md
```
