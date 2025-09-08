#!/usr/bin/env python3
"""
AI-Powered File Organizer - Main Entry Point
Intelligent file organization tool using NVIDIA NIM for content analysis.
"""

import sys
import argparse
import os
from pathlib import Path
from typing import Optional
import time
from datetime import datetime
import logging
try:
    # Ensure UTF-8 output on Windows consoles to avoid emoji encoding errors
    import sys as _sys
    _sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

from pathlib import Path as _Path

def _load_nim_models_from_config() -> dict:
    """Best-effort load of model IDs from config.yaml in CWD."""
    models = {}
    try:
        cfg_path = _Path.cwd() / 'config.yaml'
        if yaml and cfg_path.exists():
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            models = (cfg.get('nvidia_nim', {}) or {}).get('models', {}) or {}
    except Exception:
        models = {}
    return models

def _load_similarity_from_config(default_value: float = 0.5) -> float:
    try:
        cfg_path = _Path.cwd() / 'config.yaml'
        if yaml and cfg_path.exists():
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            return float(((cfg.get('ai_analysis', {}) or {}).get('similarity_threshold', default_value)))
    except Exception:
        pass
    return default_value
from nim_integration import NIMClient
from nim_integration.embeddings import LocalEmbeddingBackend, NIMEmbeddingBackend

# Import new smart semantic organizer
try:
    from smart_file_organizer import SmartFileOrganizer
    SMART_ORGANIZER_AVAILABLE = True
except ImportError:
    SMART_ORGANIZER_AVAILABLE = False


def setup_environment():
    """Set up the application environment."""
    # Create necessary directories
    directories = ['logs', 'backups', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Basic logging setup
    logging.basicConfig(level=logging.INFO)
    return True


async def organize_files_smart(source_path: str, destination_path: Optional[str] = None, dry_run: bool = False,
                               backend: Optional[str] = None, embed_model: Optional[str] = None,
                               query: Optional[str] = None, top_k: int = 10,
                               api_key: Optional[str] = None, base_url: Optional[str] = None,
                               qa: Optional[str] = None, llm_model: Optional[str] = None,
                               multimodal: bool = False, vision_model: Optional[str] = None):
    """
    Organize files using the new smart semantic detection system.
    
    Args:
        source_path: Path to source directory
        destination_path: Path to destination directory (optional)
        dry_run: If True, only show what would be done without actually moving files
    """
    print(f"🚀 Starting SMART semantic file organization...")
    print(f"Source: {source_path}")
    
    if destination_path:
        print(f"Destination: {destination_path}")
    else:
        print("Destination: Smart_Organized_Files")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be moved")
    
    try:
        # Initialize smart organizer
        # Build embedding backend
        embedding_backend = None
        selected_backend = (backend or "local").lower()
        model_name = embed_model
        if selected_backend == "nim":
            model_name = model_name or "nvidia/nv-embed-v1"
            nim_client = NIMClient(base_url=base_url, api_key=api_key)
            if not nim_client.is_configured():
                print("❌ NVIDIA NIM not configured. Set NVIDIA_API_KEY and optionally NVIDIA_NIM_BASE_URL.")
                sys.exit(1)
            try:
                # If using e5-style embeddings, set input_type='passage' for documents
                embedding_backend = NIMEmbeddingBackend(model_name, nim_client, force_e5=("e5" in model_name), input_type="passage")
                print(f"✅ Using NIM embeddings: {model_name}")
            except Exception as e:
                print(f"❌ Failed to initialize NIM backend: {e}")
                sys.exit(1)
        else:
            model_name = model_name or "all-MiniLM-L6-v2"
            embedding_backend = LocalEmbeddingBackend(model_name)
            print(f"✅ Using local embeddings: {model_name}")

        sim_threshold = _load_similarity_from_config(0.5)
        organizer = SmartFileOrganizer(
            similarity_threshold=sim_threshold,
            base_output_dir=destination_path or "Smart_Organized_Files",
            use_embeddings=True,
            embedding_backend=embedding_backend,
            enable_multimodal=multimodal,
            vision_model=vision_model,
            nim_api_key=api_key,
            nim_base_url=base_url,
        )
        
        if qa:
            result = await organizer.semantic_qa([source_path], question=qa, top_k=top_k,
                                                llm_model=llm_model or "meta/llama3-70b-instruct",
                                                api_key=api_key, base_url=base_url)
            print("\n🧠 Q&A:")
            print(result.get('answer', ''))
            if result.get('top_context'):
                print("\nContext files:")
                for p in result['top_context']:
                    print(f" - {p}")
        elif query:
            result = await organizer.semantic_search([source_path], query=query, top_k=top_k)
            print("\n🔎 Semantic search results:")
            for item in result.get('results', []):
                print(f"   {item['score']:.4f}  {item['path']}")
        else:
            # Execute smart organization
            result = await organizer.organize_files(
                source_paths=[source_path],
                destination_dir=destination_path,
                dry_run=dry_run
            )
        
        if 'error' in result:
            print(f"❌ Smart organization failed: {result['error']}")
            print("   Falling back to basic organization...")
            return organize_files_basic(source_path, destination_path, dry_run)
        
        # Display results
        stats = result['statistics']
        print(f"\n✅ SMART ORGANIZATION {'SIMULATION' if dry_run else 'COMPLETE'}")
        print(f"   Projects detected: {stats['total_projects_detected']}")
        print(f"   Files processed: {stats['total_files_processed']}")
        print(f"   Success rate: {stats['successful_operations']}/{stats['total_files_processed']}")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
        
        if 'undo_file' in result:
            print(f"   Undo file: {result['undo_file']}")
        
        print(f"\n📊 PROJECT BREAKDOWN:")
        for project_type, count in result['project_breakdown']['by_type'].items():
            print(f"   {project_type}: {count} projects")
            
        print(f"\n🎯 DETECTED PROJECTS:")
        for project in result['detected_projects']:
            print(f"   • {project['name']} ({project['file_count']} files, confidence: {project['confidence']})")
        
        return result
        
    except Exception as e:
        print(f"❌ Smart organization failed: {e}")
        print("   Falling back to basic organization...")
        return organize_files_basic(source_path, destination_path, dry_run)

def organize_files_basic(source_path: str, destination_path: Optional[str] = None, dry_run: bool = False):
    """
    Basic file organization using traditional methods.
    
    Args:
        source_path: Path to source directory
        destination_path: Path to destination directory (optional)
        dry_run: If True, only show what would be done without actually moving files
    """
    print("❌ Basic mode is not available in this build. Use smart mode (default).")
    return

def organize_files(source_path: str, destination_path: Optional[str] = None, dry_run: bool = False, use_smart: bool = True,
                   backend: Optional[str] = None, embed_model: Optional[str] = None,
                   query: Optional[str] = None, top_k: int = 10,
                   api_key: Optional[str] = None, base_url: Optional[str] = None,
                   qa: Optional[str] = None, llm_model: Optional[str] = None,
                   multimodal: bool = False, vision_model: Optional[str] = None):
    """
    Main organize function - can use smart semantic detection or fall back to basic.
    
    Args:
        source_path: Path to source directory
        destination_path: Path to destination directory (optional)
        dry_run: If True, only show what would be done without actually moving files
        use_smart: If True, use smart semantic organization (default)
    """
    
    if use_smart and SMART_ORGANIZER_AVAILABLE:
        # Use new smart semantic organization
        import asyncio
        return asyncio.run(organize_files_smart(source_path, destination_path, dry_run, backend=backend, embed_model=embed_model, query=query, top_k=top_k, api_key=api_key, base_url=base_url, qa=qa, llm_model=llm_model, multimodal=multimodal, vision_model=vision_model))
    else:
        # Use basic organization
        if use_smart and not SMART_ORGANIZER_AVAILABLE:
            print("⚠️  Smart organizer not available, using basic organization")
        return organize_files_basic(source_path, destination_path, dry_run)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-Powered File Organizer - Intelligent file organization using NVIDIA NIM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source ~/Downloads
  %(prog)s --source ~/Downloads --destination ~/Organized
  %(prog)s --source ~/Downloads --dry-run
  %(prog)s --source ~/Downloads --destination ~/Organized --verbose
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Source directory to organize'
    )
    
    parser.add_argument(
        '--destination', '-d',
        help='Destination directory (default: organize in place)'
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without actually moving files'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Custom configuration file path'
    )
    
    parser.add_argument(
        '--basic',
        action='store_true',
        help='Use basic organization instead of smart semantic detection'
    )

    parser.add_argument(
        '--backend',
        choices=['local', 'nim'],
        help='Embedding backend to use (default: local)'
    )

    parser.add_argument(
        '--embed-model',
        help='Embedding model name (local or NIM model identifier)'
    )

    parser.add_argument(
        '--query',
        help='Run semantic search instead of organizing (provide natural language query)'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Number of results to return for semantic search'
    )

    parser.add_argument(
        '--multimodal',
        action='store_true',
        help='Enable multimodal analysis (placeholder; future enhancement)'
    )

    parser.add_argument(
        '--vision-model',
        help='NIM vision model to use when --multimodal is set'
    )

    parser.add_argument(
        '--qa',
        help='Run semantic Q&A over your files (retrieval + NIM LLM)'
    )

    parser.add_argument(
        '--llm-model',
        help='NIM LLM model for --qa (default: meta/llama3-70b-instruct)'
    )

    parser.add_argument(
        '--api-key',
        help='Override NVIDIA_API_KEY for this run'
    )

    parser.add_argument(
        '--base-url',
        help='Override NVIDIA_NIM_BASE_URL for this run'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Smart Semantic File Organizer v2.0.0'
    )
    
    args = parser.parse_args()

    # Fill defaults from config.yaml models if not provided
    nm = _load_nim_models_from_config()
    if not args.embed_model and 'embeddings' in nm:
        args.embed_model = nm['embeddings']
    if not args.llm_model and 'text_analysis' in nm:
        args.llm_model = nm['text_analysis']
    if not args.vision_model and 'image_analysis' in nm:
        args.vision_model = nm['image_analysis']
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Note: config file support for the legacy 'src' package is disabled in this build
    
    # Print banner
    if args.basic or not SMART_ORGANIZER_AVAILABLE:
        print("🤖 AI-Powered File Organizer v2.0.0 (Basic Mode)")
        print("   Traditional file type organization")
    else:
        print("🧠 Smart Semantic File Organizer v2.0.0")
        print("   Intelligent cross-format project detection")
    print("=" * 50)
    
    # Set up environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Validate source path
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        print(f"❌ Source directory does not exist: {source_path}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"❌ Source path is not a directory: {source_path}")
        sys.exit(1)
    
    # Validate destination path if provided
    destination_path = None
    if args.destination:
        destination_path = Path(args.destination).expanduser().resolve()
        if destination_path.exists() and not destination_path.is_dir():
            print(f"❌ Destination path exists but is not a directory: {destination_path}")
            sys.exit(1)
    
    try:
        # Run organization
        organize_files(
            source_path=str(source_path),
            destination_path=str(destination_path) if destination_path else None,
            dry_run=args.dry_run,
            use_smart=not args.basic and SMART_ORGANIZER_AVAILABLE,
            backend=args.backend,
            embed_model=args.embed_model,
            query=args.query,
            top_k=args.top_k,
            api_key=args.api_key,
            base_url=args.base_url,
            qa=args.qa,
            llm_model=args.llm_model,
            multimodal=args.multimodal,
            vision_model=args.vision_model
        )
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 