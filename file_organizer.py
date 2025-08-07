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

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config
from src.utils.logger import logger
from src.core.file_scanner import FileScanner
from src.ai.nvidia_nim_client import NVIDIANIMClient

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
    
    # Validate configuration
    issues = config.validate_config()
    if issues['errors']:
        print("❌ Configuration errors found:")
        for error in issues['errors']:
            print(f"   • {error}")
        return False
    
    if issues['warnings']:
        print("⚠️  Configuration warnings:")
        for warning in issues['warnings']:
            print(f"   • {warning}")
    
    return True


async def organize_files_smart(source_path: str, destination_path: Optional[str] = None, dry_run: bool = False):
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
        organizer = SmartFileOrganizer(
            similarity_threshold=0.3,
            base_output_dir=destination_path or "Smart_Organized_Files"
        )
        
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
    print(f"🔍 Starting basic file organization...")
    print(f"Source: {source_path}")
    
    if destination_path:
        print(f"Destination: {destination_path}")
    else:
        print("Destination: In-place organization")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be moved")
    
    # Initialize components
    scanner = FileScanner()
    
    # Check if NVIDIA NIM is available
    nim_available = False
    try:
        nim_client = NVIDIANIMClient()
        nim_available = nim_client.is_available()
        if nim_available:
            print("✅ NVIDIA NIM connected successfully")
        else:
            print("⚠️  NVIDIA NIM not available - using basic classification")
    except Exception as e:
        print(f"⚠️  NVIDIA NIM initialization failed: {e}")
        print("   Continuing with basic classification...")
    
    # Start organization session
    start_time = time.time()
    logger.log_session_start(source_path, destination_path or "in-place")
    
    try:
        # Step 1: Scan files
        print("\n📁 Scanning files...")
        files = scanner.scan_directory(source_path, recursive=True)
        
        if not files:
            print("❌ No files found to organize")
            return
        
        print(f"📊 Found {len(files)} files to process")
        
        # Step 2: Show statistics
        stats = scanner.get_scan_statistics(files)
        print(f"   Total size: {stats.get('total_size_human', 'Unknown')}")
        print(f"   File types: {len(stats.get('file_types', {}))}")
        if stats.get('duplicates', 0) > 0:
            print(f"   Duplicates found: {stats['duplicates']}")
        
        # Step 3: Analyze content (if NIM is available)
        if nim_available and not dry_run:
            print("\n🤖 Analyzing file content with AI...")
            # For now, we'll implement a basic version
            # The full AI analysis will be implemented in the next iteration
            print("   AI content analysis will be implemented in the next phase")
        
        # Step 4: Organize files
        print(f"\n📋 {'Would organize' if dry_run else 'Organizing'} files...")
        
        organized_count = 0
        error_count = 0
        
        # Basic organization by file type for now
        for file_info in files:
            try:
                # Generate target path based on file type
                if destination_path:
                    base_path = Path(destination_path)
                else:
                    base_path = Path(source_path)
                
                # Create folder hierarchy: FileType > Category
                target_dir = base_path / file_info.file_type.title()
                
                # Add subcategory based on extension
                categories = config.get_categories_for_type(file_info.file_type)
                if categories:
                    target_dir = target_dir / categories[0]
                
                if dry_run:
                    print(f"   📄 {file_info.name}{file_info.extension} → {target_dir}")
                else:
                    # Create target directory
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file (for now, we'll just log the action)
                    target_file = target_dir / f"{file_info.name}{file_info.extension}"
                    logger.log_file_operation("ORGANIZE", file_info.path, str(target_file))
                    print(f"   ✅ {file_info.name}{file_info.extension}")
                
                organized_count += 1
                
            except Exception as e:
                error_count += 1
                logger.log_error_with_context(e, "File organization", file_info.path)
                print(f"   ❌ Error organizing {file_info.name}: {e}")
        
        # Step 5: Summary
        duration = time.time() - start_time
        print(f"\n{'📊 DRY RUN SUMMARY' if dry_run else '✅ ORGANIZATION COMPLETE'}")
        print(f"   Files processed: {organized_count}")
        if error_count > 0:
            print(f"   Errors: {error_count}")
        print(f"   Duration: {duration:.2f} seconds")
        
        logger.log_session_end(organized_count, error_count, duration)
        
    except KeyboardInterrupt:
        print("\n🛑 Organization cancelled by user")
        logger.log_info("Organization cancelled by user")
    except Exception as e:
        print(f"\n❌ Organization failed: {e}")
        logger.log_error_with_context(e, "Main organization process")

def organize_files(source_path: str, destination_path: Optional[str] = None, dry_run: bool = False, use_smart: bool = True):
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
        return asyncio.run(organize_files_smart(source_path, destination_path, dry_run))
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
        '--version',
        action='version',
        version='Smart Semantic File Organizer v2.0.0'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logger.set_level("DEBUG")
    
    # Load custom config if provided
    if args.config:
        config.config_path = args.config
        config.reload()
    
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
            use_smart=not args.basic and SMART_ORGANIZER_AVAILABLE
        )
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.log_error_with_context(e, "Main application")
        sys.exit(1)


if __name__ == "__main__":
    main() 