# File Organizer with NVIDIA NIM Integration

This project is an AI-powered file organization tool that uses NVIDIA NIM (NVIDIA Inference Microservices) for intelligent content analysis and classification.

## Features

- Intelligent file classification using NVIDIA NIM
- Support for multiple file types:
  - Documents (PDF, DOC, DOCX, TXT)
  - Images (JPG, JPEG, PNG, GIF)
  - Audio (MP3, WAV, OGG)
  - Video (MP4, AVI, MOV)
- Configurable content analysis settings
- Fallback to basic classification when NIM is unavailable
- Comprehensive logging and error handling

## Prerequisites

- Python 3.8 or higher
- NVIDIA NIM API key
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd file-organizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your NVIDIA NIM API key:
   - Create a `.env` file in the project root
   - Add your API key: `NVIDIA_NIM_API_KEY=your-api-key-here`

## Configuration

The NIM integration can be configured through `config/nim_config.yaml`. Key settings include:

- API configuration (base URL, version, timeout)
- Content analysis settings (confidence threshold, file size limits)
- Supported file types and their corresponding NIM models
- Fallback behavior

Example configuration:
```yaml
api:
  base_url: "https://api.nvcf.nvidia.com"
  version: "v1"
  timeout_seconds: 30

content_analysis:
  min_confidence: 0.7
  max_file_size: 104857600  # 100MB
  supported_types:
    documents:
      - pdf
      - doc
      - docx
      - txt
      model: "llama2-70b"
```

## Usage

The NIM service can be used programmatically:

```python
from nim_service import NIMService

# Initialize the service
nim_service = NIMService()

# Classify a file
categories = await nim_service.classify_file("path/to/file.pdf")
if categories:
    print(f"File categories: {categories}")
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Error Handling

The NIM integration includes robust error handling:

- Graceful degradation when NIM is unavailable
- File size limit enforcement
- Configurable fallback to basic classification
- Failed request storage for retry (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

[Your License Here] 