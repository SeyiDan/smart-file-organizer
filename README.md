# 🧠 Smart Semantic File Organizer

An intelligent file organization system that understands **what files mean together** and groups them into semantic projects, rather than just organizing by file type.

## ✨ What Makes This Different

### Traditional Organizers:
```
Downloads/
├── PDFs/ (all PDFs together, regardless of purpose)
├── Images/ (all images together, regardless of context)  
└── Audio/ (all audio together, regardless of project)
```

### Smart Semantic Organizer:
```
Organized_Files/
├── Music_Project_Recording/
│   ├── Songs/
│   │   ├── By_Artist/Beatles/
│   │   └── By_Artist/Queen/
│   ├── Album_Art/
│   │   ├── band_photo.jpg
│   │   └── album_cover.png
│   └── Lyrics_Notes/
│       ├── lyrics_draft.txt
│       └── recording_notes.md
│
└── Academic_Project_Research/
    ├── Papers_Documents/
    │   ├── Drafts/
    │   ├── Final_Documents/
    │   └── Research_Materials/
    ├── Figures_Images/
    └── Presentations/
```

## 🚀 Key Features

### 🔍 Semantic Analysis
- **Content Understanding**: Reads document text, audio metadata, image EXIF data
- **Cross-Format Intelligence**: Groups `song.mp3` + `album_art.jpg` + `lyrics.txt` = Same project
- **Contextual Keywords**: Detects themes like "music", "academic", "work", "photos"

### 🎯 Project Detection
- **Multi-File Relationships**: Finds files that belong together by meaning
- **Progressive Classification**: Project → Type → Attributes → Files
- **Dynamic Hierarchy**: Creates folder structures based on discovered content patterns

### ⚡ Smart Organization
- **Confidence Scoring**: Shows how sure the system is about groupings
- **Undo System**: Complete rollback capability for any organization
- **Dry Run Mode**: Preview organization before making changes
- **Multiple File Types**: Documents, Images, Audio, Video, Archives

## 📋 Prerequisites

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/smart-file-organizer.git
cd smart-file-organizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Download NLTK data for enhanced text processing:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## 🎮 Usage

### Command Line Interface

```bash
# Basic organization with preview
python file_organizer.py --source ~/Downloads --dry-run

# Organize files to a specific destination
python file_organizer.py --source ~/Downloads --destination ~/Organized

# Use basic organization (by file type only)
python file_organizer.py --source ~/Downloads --basic

# Verbose output for debugging
python file_organizer.py --source ~/Downloads --verbose
```

### Programmatic Usage

```python
from smart_file_organizer import SmartFileOrganizer

# Initialize the organizer
organizer = SmartFileOrganizer(similarity_threshold=0.3)

# Organize files with semantic analysis
results = await organizer.organize_files(
    source_paths=["~/Downloads"],
    destination_dir="~/Organized",
    dry_run=True  # Preview first
)

# Check results
if results.get('success'):
    print(f"Organized {results['files_moved']} files into {results['projects_created']} projects")
```

## ⚙️ Configuration

The system can be configured through `config.yaml`:

```yaml
# Semantic analysis settings
semantic:
  similarity_threshold: 0.3
  min_files_per_project: 2
  confidence_threshold: 0.7

# File type support
supported_extensions:
  documents: ['.pdf', '.docx', '.txt', '.md']
  images: ['.jpg', '.jpeg', '.png', '.gif']
  audio: ['.mp3', '.wav', '.flac']
  video: ['.mp4', '.avi', '.mov']
  archives: ['.zip', '.rar', '.7z']

# Organization preferences
organization:
  create_date_folders: true
  preserve_structure: false
  max_depth: 4
```

## 🔧 Core Components

- **`semantic_analyzer.py`**: Extracts meaning from file content and metadata
- **`project_detector.py`**: Groups related files into semantic projects
- **`hierarchy_builder.py`**: Creates organized folder structures
- **`smart_file_organizer.py`**: Main orchestrator class
- **`file_organizer.py`**: Command-line interface

## 🧪 Testing

The project includes comprehensive test scenarios:

```bash
# Run test scenarios
python test_scenarios.py

# Demo the smart organizer
python demo_smart_organizer.py
```

## 📊 How It Works

1. **File Discovery**: Scans source directories for all supported file types
2. **Content Analysis**: Extracts text, metadata, and contextual information
3. **Semantic Grouping**: Uses ML similarity algorithms to find related files
4. **Project Detection**: Identifies coherent projects with confidence scores
5. **Hierarchy Building**: Creates meaningful folder structures
6. **Safe Execution**: Moves files with full undo capability

## 🛡️ Safety Features

- **Dry Run Mode**: Preview all changes before execution
- **Undo System**: Complete rollback capability with JSON-based undo files
- **Backup Creation**: Automatic backups before major operations
- **Conflict Resolution**: Smart handling of duplicate filenames
- **Progress Tracking**: Real-time feedback with progress bars

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python's powerful machine learning ecosystem
- Uses NLTK for natural language processing
- Leverages scikit-learn for similarity analysis
- Rich terminal output powered by the `rich` library