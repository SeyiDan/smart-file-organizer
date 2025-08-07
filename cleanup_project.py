#!/usr/bin/env python3
"""
Project Cleanup Script
Removes unnecessary files and keeps only the essential smart organizer components.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove unnecessary files and directories"""
    
    print("🧹 Smart File Organizer - Project Cleanup")
    print("=" * 50)
    
    # Files to remove
    files_to_remove = [
        "auth_manager.py",
        "demo_smart_innovation.py", 
        "innovation_results.txt",
        "quick_demo.py",
        "main.py",
        "content_analyzer.py",
        "nim_service.py", 
        "file_classifier.py",
        "config_private.yaml",
        "HYBRID_APPROACH.md",
        "create_safe_test_files.py"
    ]
    
    # Directories to remove  
    dirs_to_remove = [
        "example_files",
        "examples", 
        "test_files",
        "config"  # Will consolidate into main config.yaml
    ]
    
    # Track what was removed
    removed_files = []
    removed_dirs = []
    
    print("🗑️  Removing unnecessary files...")
    
    # Remove files
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                removed_files.append(file_name)
                print(f"   ✅ Removed: {file_name}")
            except Exception as e:
                print(f"   ❌ Could not remove {file_name}: {e}")
        else:
            print(f"   ℹ️  Not found: {file_name}")
    
    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                removed_dirs.append(dir_name)
                print(f"   ✅ Removed directory: {dir_name}")
            except Exception as e:
                print(f"   ❌ Could not remove {dir_name}: {e}")
        else:
            print(f"   ℹ️  Not found: {dir_name}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   Files removed: {len(removed_files)}")
    print(f"   Directories removed: {len(removed_dirs)}")
    
    print(f"\n🎯 Essential files remaining:")
    essential_files = [
        "semantic_analyzer.py",
        "project_detector.py", 
        "hierarchy_builder.py",
        "smart_file_organizer.py",
        "safe_smart_organizer.py",
        "file_organizer.py",
        "demo_smart_organizer.py",
        "test_scenarios.py",
        "requirements.txt",
        "config.yaml",
        "SMART_ORGANIZER_GUIDE.md"
    ]
    
    for file_name in essential_files:
        if Path(file_name).exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ MISSING: {file_name}")
    
    print(f"\n🎉 Cleanup complete! Your project is now streamlined.")
    print(f"💡 You can now focus on the essential smart organizer components.")

def show_current_structure():
    """Show current project structure"""
    print("\n📁 Current project structure:")
    
    for item in sorted(Path('.').iterdir()):
        if item.name.startswith('.'):
            continue
            
        if item.is_file():
            size = item.stat().st_size
            if size > 1024:
                size_str = f"{size // 1024}KB"
            else:
                size_str = f"{size}B"
            print(f"   📄 {item.name} ({size_str})")
        elif item.is_dir():
            try:
                file_count = len([f for f in item.rglob('*') if f.is_file()])
                print(f"   📁 {item.name}/ ({file_count} files)")
            except:
                print(f"   📁 {item.name}/")

def main():
    """Main cleanup function"""
    print("Current state:")
    show_current_structure()
    
    print(f"\n⚠️  This will remove unnecessary files from your project.")
    print(f"   Your core smart organizer functionality will be preserved.")
    
    response = input(f"\n🤔 Proceed with cleanup? [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        cleanup_project()
    else:
        print("🛑 Cleanup cancelled.")

if __name__ == "__main__":
    main()