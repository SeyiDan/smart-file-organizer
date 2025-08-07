#!/usr/bin/env python3
"""
Safe Smart Organizer - Enhanced safety wrapper
Provides multiple verification steps before touching your real files.
"""

import os
import shutil
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from smart_file_organizer import SmartFileOrganizer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SafeSmartOrganizer:
    """Wrapper that provides enhanced safety for file organization"""
    
    def __init__(self, similarity_threshold: float = 0.3):
        self.organizer = SmartFileOrganizer(similarity_threshold)
        self.test_suffix = f"_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def safe_organize_workflow(self, source_path: str, destination_path: str = None):
        """
        Complete safe workflow with multiple verification steps.
        """
        source_path = Path(source_path).expanduser().resolve()
        
        if not source_path.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return False
            
        print("🛡️  SAFE SMART ORGANIZER")
        print("=" * 50)
        print(f"Source: {source_path}")
        print(f"This workflow ensures your files are safe!\n")
        
        # Step 1: Analysis only (no file operations)
        print("📊 STEP 1: Analyzing your files...")
        analysis = await self._analyze_only(source_path)
        
        if not analysis:
            print("❌ No projects detected. Nothing to organize.")
            return False
            
        if not self._confirm_analysis(analysis):
            print("🛑 Analysis cancelled by user.")
            return False
            
        # Step 2: Create test copy and organize it
        print("\n🧪 STEP 2: Testing organization on a copy...")
        test_success = await self._test_organization(source_path, analysis)
        
        if not test_success:
            print("❌ Test organization failed.")
            return False
            
        if not self._confirm_test_results():
            print("🛑 Test results not approved by user.")
            return False
            
        # Step 3: Apply to real files (with undo capability)
        print("\n🎯 STEP 3: Applying to your real files...")
        real_success = await self._apply_to_real_files(source_path, destination_path)
        
        if real_success:
            print("\n✅ SAFE ORGANIZATION COMPLETED!")
            print("🔄 Undo information has been saved.")
            print("📁 Your original files have been safely organized.")
            return True
        else:
            print("❌ Real file organization failed.")
            return False
    
    async def _analyze_only(self, source_path: Path):
        """Step 1: Analyze files without any operations"""
        try:
            result = await self.organizer.analyze_files_only([str(source_path)])
            
            if 'error' in result:
                logger.error(f"Analysis failed: {result['error']}")
                return None
                
            if result.get('projects_detected', 0) == 0:
                return None
                
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return None
    
    def _confirm_analysis(self, analysis):
        """Show analysis results and get user confirmation"""
        print(f"\n📋 ANALYSIS RESULTS:")
        print(f"   Files analyzed: {analysis['files_analyzed']}")
        print(f"   Projects detected: {analysis['projects_detected']}")
        
        print(f"\n🎯 DETECTED PROJECTS:")
        for project in analysis['projects']:
            print(f"   • {project['name']}")
            print(f"     Type: {project['type']}")
            print(f"     Files: {project['files']}")
            print(f"     Confidence: {project['confidence']:.2f}")
            
            # Show structure preview
            print(f"     Structure:")
            for folder, contents in project['structure'].items():
                if isinstance(contents, list):
                    print(f"       📁 {folder}/ ({len(contents)} files)")
                elif isinstance(contents, dict):
                    print(f"       📁 {folder}/ ({len(contents)} subfolders)")
            print()
        
        while True:
            response = input("🤔 Do these groupings look correct? [y/N/details]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            elif response in ['d', 'details']:
                self._show_detailed_structure(analysis)
            else:
                print("Please answer 'y' for yes, 'n' for no, or 'd' for details")
    
    def _show_detailed_structure(self, analysis):
        """Show detailed file-by-file structure"""
        print(f"\n📄 DETAILED STRUCTURE:")
        for project in analysis['projects']:
            print(f"\n🎯 {project['name']}:")
            for folder, contents in project['structure'].items():
                print(f"  📁 {folder}/")
                if isinstance(contents, list):
                    for file_path in contents:
                        filename = Path(file_path).name
                        print(f"    📄 {filename}")
                elif isinstance(contents, dict):
                    for subfolder, subcontents in contents.items():
                        print(f"    📁 {subfolder}/")
                        if isinstance(subcontents, list):
                            for file_path in subcontents:
                                filename = Path(file_path).name
                                print(f"      📄 {filename}")
    
    async def _test_organization(self, source_path: Path, analysis):
        """Step 2: Create test copy and organize it"""
        # Create test copy
        test_source = source_path.parent / f"{source_path.name}{self.test_suffix}"
        test_destination = source_path.parent / f"ORGANIZED{self.test_suffix}"
        
        try:
            print(f"   Creating test copy: {test_source}")
            shutil.copytree(source_path, test_source)
            
            print(f"   Testing organization...")
            result = await self.organizer.organize_files(
                source_paths=[str(test_source)],
                destination_dir=str(test_destination),
                dry_run=False
            )
            
            if 'error' in result:
                logger.error(f"Test organization failed: {result['error']}")
                return False
                
            print(f"   ✅ Test completed successfully!")
            print(f"   📁 Test results in: {test_destination}")
            
            # Store paths for cleanup later
            self.test_source = test_source
            self.test_destination = test_destination
            
            return True
            
        except Exception as e:
            logger.error(f"Test organization error: {e}")
            return False
    
    def _confirm_test_results(self):
        """Show test results and get user confirmation"""
        print(f"\n🔍 TEST RESULTS READY!")
        print(f"   Test organized files: {self.test_destination}")
        print(f"   Please examine the organization structure.")
        
        input(f"\n📂 Press Enter after you've examined the test results...")
        
        while True:
            response = input("✅ Are you satisfied with the test organization? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please answer 'y' for yes or 'n' for no")
    
    async def _apply_to_real_files(self, source_path: Path, destination_path: str = None):
        """Step 3: Apply organization to real files"""
        if not destination_path:
            destination_path = str(source_path.parent / f"{source_path.name}_ORGANIZED")
        
        try:
            print(f"   Organizing real files...")
            print(f"   Source: {source_path}")
            print(f"   Destination: {destination_path}")
            
            result = await self.organizer.organize_files(
                source_paths=[str(source_path)],
                destination_dir=destination_path,
                dry_run=False
            )
            
            if 'error' in result:
                logger.error(f"Real organization failed: {result['error']}")
                return False
                
            # Show undo information
            if 'undo_file' in result:
                print(f"\n🔄 UNDO INFORMATION:")
                print(f"   Undo file: {result['undo_file']}")
                print(f"   To undo: python -c \"from smart_file_organizer import SmartFileOrganizer; SmartFileOrganizer().undo_organization('{result['undo_file']}')\"")
            
            return True
            
        except Exception as e:
            logger.error(f"Real organization error: {e}")
            return False
        finally:
            # Cleanup test files
            self._cleanup_test_files()
    
    def _cleanup_test_files(self):
        """Clean up test files after completion"""
        try:
            if hasattr(self, 'test_source') and self.test_source.exists():
                shutil.rmtree(self.test_source)
                print(f"   🧹 Cleaned up test copy")
                
            if hasattr(self, 'test_destination') and self.test_destination.exists():
                shutil.rmtree(self.test_destination)
                print(f"   🧹 Cleaned up test results")
                
        except Exception as e:
            logger.warning(f"Could not clean up test files: {e}")

async def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe Smart File Organizer")
    parser.add_argument('--source', '-s', required=True, help='Source directory to organize')
    parser.add_argument('--destination', '-d', help='Destination directory (optional)')
    parser.add_argument('--threshold', '-t', type=float, default=0.3, help='Similarity threshold (0.1-0.8)')
    
    args = parser.parse_args()
    
    organizer = SafeSmartOrganizer(similarity_threshold=args.threshold)
    success = await organizer.safe_organize_workflow(args.source, args.destination)
    
    if success:
        print("\n🎉 Safe organization completed successfully!")
    else:
        print("\n❌ Organization was cancelled or failed.")

if __name__ == "__main__":
    asyncio.run(main())