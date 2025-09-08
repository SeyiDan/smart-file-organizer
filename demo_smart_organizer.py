#!/usr/bin/env python3
"""
Demo Script for Smart Semantic File Organizer
Shows off the innovative cross-format project detection capabilities.
"""

import asyncio
import logging
import os
from pathlib import Path
import json
from typing import List

from smart_file_organizer import SmartFileOrganizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_with_safe_test_area():
    """
    Demo the smart organizer using your existing safe_test_area directory.
    This will show how it groups files by semantic meaning rather than just type.
    """
    print(" Smart Semantic File Organizer Demo")
    print("=" * 60)
    
    # Use your existing safe test area
    test_dir = "safe_test_area"
    
    if not os.path.exists(test_dir):
        print(f" Test directory '{test_dir}' not found!")
        print("Please ensure you're running from the project root")
        return
    
    # Initialize the smart organizer
    organizer = SmartFileOrganizer(
        similarity_threshold=0.2,  # Lower threshold for demo
        base_output_dir="Smart_Organized_Demo"
    )
    
    print(f"\n Analyzing files in '{test_dir}'...")
    
    # First, just analyze to show what it would detect
    analysis_result = await organizer.analyze_files_only([test_dir])
    
    if 'error' in analysis_result:
        print(f" Analysis failed: {analysis_result['error']}")
        return
    
    if 'message' in analysis_result:
        print(f"  {analysis_result['message']}")
        print("   (This is normal for small/unrelated file sets)")
        
        # Show basic file breakdown instead
        files = []
        for file_path in Path(test_dir).rglob('*'):
            if file_path.is_file():
                files.append(str(file_path))
        
        print(f"\n Found {len(files)} files:")
        file_types = {}
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            
        for ext, count in sorted(file_types.items()):
            print(f"   {ext}: {count} files")
            
        return
    
    # Show analysis results
    print(f"\n Semantic Analysis Results:")
    print(f"   Files analyzed: {analysis_result['files_analyzed']}")
    print(f"   Projects detected: {analysis_result['projects_detected']}")
    
    if analysis_result['projects_detected'] > 0:
        print(f"\n Detected Projects:")
        for project in analysis_result['projects']:
            print(f"\n    {project['name']}")
            print(f"      Type: {project['type']}")
            print(f"      Files: {project['files']}")
            print(f"      Confidence: {project['confidence']}")
            print(f"      Structure preview:")
            
            # Show structure preview
            structure = project['structure']
            for folder, contents in structure.items():
                if isinstance(contents, list):
                    print(f"          {folder}/ ({len(contents)} files)")
                    for file_path in contents[:3]:  # Show first 3 files
                        file_name = Path(file_path).name
                        print(f"             {file_name}")
                    if len(contents) > 3:
                        print(f"            ... and {len(contents) - 3} more")
                elif isinstance(contents, dict):
                    print(f"          {folder}/")
                    for subfolder, subcontents in contents.items():
                        if isinstance(subcontents, list):
                            print(f"             {subfolder}/ ({len(subcontents)} files)")
        
        # Ask if user wants to proceed with organization
        print(f"\n Would you like to proceed with organizing these files?")
        print("   This will create the Smart_Organized_Demo directory with the new structure.")
        
        response = input("   Continue? [y/N]: ").strip().lower()
        
        if response == 'y' or response == 'yes':
            print(f"\n Executing smart organization...")
            
            # Execute the organization (not a dry run)
            org_result = await organizer.organize_files(
                source_paths=[test_dir],
                dry_run=False
            )
            
            if 'error' not in org_result:
                print(f"\n Organization completed!")
                print(f"   Projects organized: {org_result['statistics']['total_projects_detected']}")
                print(f"   Files processed: {org_result['statistics']['total_files_processed']}")
                print(f"   Success rate: {org_result['statistics']['successful_operations']}/{org_result['statistics']['total_files_processed']}")
                
                if 'undo_file' in org_result:
                    print(f"   Undo file saved: {org_result['undo_file']}")
                    print(f"   To undo: python -c \"import asyncio; from demo_smart_organizer import undo_demo; asyncio.run(undo_demo('{org_result['undo_file']}'))\"")
                
                print(f"\n Check the 'Smart_Organized_Demo' directory to see your semantically organized files!")
            else:
                print(f" Organization failed: {org_result['error']}")
        else:
            print("   Organization cancelled.")
    
    print(f"\n Demo completed!")

async def undo_demo(undo_file: str):
    """Undo a previous demo organization"""
    organizer = SmartFileOrganizer()
    result = organizer.undo_organization(undo_file)
    
    if 'error' not in result:
        print(f" Undo completed: {result['successful_operations']} operations reversed")
    else:
        print(f" Undo failed: {result['error']}")

async def create_demo_scenarios():
    """
    Create some demo file scenarios to better show the semantic organization.
    This creates example files that would group well together.
    """
    print(" Creating demo scenarios...")
    
    demo_dir = Path("demo_scenarios")
    demo_dir.mkdir(exist_ok=True)
    
    # Scenario 1: Music project
    music_files = [
        "band_photo.jpg",
        "album_cover.png", 
        "song1_recording.mp3",
        "song2_demo.wav",
        "lyrics_draft.txt",
        "chord_chart.pdf",
        "recording_notes.md"
    ]
    
    for file_name in music_files:
        file_path = demo_dir / file_name
        with open(file_path, 'w') as f:
            if 'lyrics' in file_name:
                f.write("Verse 1: Music brings us together\nChorus: In harmony we stand\nBridge: Playing our song for the world\n")
            elif 'notes' in file_name:
                f.write("# Recording Session Notes\n\nBand: Demo Band\nSongs recorded: 2\nStudio: Home Studio\nNext steps: Mix and master\n")
            elif 'chord' in file_name:
                f.write("Song chord charts for album recording session\n")
            else:
                f.write(f"Demo content for {file_name}")
    
    # Scenario 2: Academic project  
    academic_files = [
        "research_paper_draft.docx",
        "final_submission.pdf",
        "data_analysis.xlsx", 
        "figure1_chart.png",
        "figure2_graph.jpg",
        "bibliography.txt",
        "presentation.pptx"
    ]
    
    for file_name in academic_files:
        file_path = demo_dir / file_name
        with open(file_path, 'w') as f:
            if 'research' in file_name or 'paper' in file_name:
                f.write("Title: Impact of Technology on Education\nAbstract: This research study examines...\nKeywords: education, technology, learning")
            elif 'bibliography' in file_name:
                f.write("References:\n1. Smith, J. (2023). Educational Technology Research\n2. Jones, M. (2022). Digital Learning Methods")
            else:
                f.write(f"Academic content for {file_name}")
    
    print(f" Created demo scenarios in '{demo_dir}'")
    print("   Run the demo again with this directory to see better semantic grouping!")
    
    return str(demo_dir)

async def main():
    """Main demo function"""
    print(" Smart Semantic File Organizer")
    print("   Your innovative cross-format project detection system!")
    print("")
    
    # Check if we should create demo scenarios
    if not os.path.exists("safe_test_area") or len(list(Path("safe_test_area").glob("*"))) < 5:
        print(" Creating demo scenarios for better demonstration...")
        demo_dir = await create_demo_scenarios()
        
        organizer = SmartFileOrganizer(similarity_threshold=0.2)
        
        print(f"\n Analyzing demo scenarios...")
        result = await organizer.analyze_files_only([demo_dir])
        
        if 'projects_detected' in result and result['projects_detected'] > 0:
            print(f"\n Found {result['projects_detected']} semantic projects!")
            
            # Show what would be organized
            org_result = await organizer.organize_files([demo_dir], dry_run=True)
            
            if 'error' not in org_result:
                print(f"\n Organization Preview:")
                for project in org_result['detected_projects']:
                    print(f"    {project['name']} ({project['type']} project)")
                    print(f"      Confidence: {project['confidence']}")
                    for folder, content in project['structure_preview'].items():
                        print(f"          {folder}: {content}")
                    print()
    else:
        # Use existing safe test area
        await demo_with_safe_test_area()

if __name__ == "__main__":
    asyncio.run(main())
