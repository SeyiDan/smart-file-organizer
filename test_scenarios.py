#!/usr/bin/env python3
"""
Create test scenarios to demonstrate the smart organizer capabilities.
Run this to create realistic test files that show semantic grouping.
"""

import os
from pathlib import Path
import json

def create_music_project():
    """Create a realistic music project with mixed file types"""
    base_dir = Path("test_scenarios/scattered_files")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Music project files
    files = {
        "band_rehearsal_photo.jpg": "Photo of band during rehearsal session for new album",
        "album_cover_draft.png": "Draft design for album cover artwork", 
        "track01_demo.mp3": "Demo recording of first song",
        "track02_rough_mix.wav": "Rough mix of second track",
        "lyrics_chorus_ideas.txt": "Verse 1: Music flows through our souls\nChorus: We're recording our dreams tonight\nBridge: In the studio where magic happens\n\nArtist: The Dream Band\nAlbum: Night Sessions",
        "chord_progressions.md": "# Song Chord Charts\n\n## Track 1 - Dream Flow\nVerse: Am - F - C - G\nChorus: F - G - Am - F\n\n## Track 2 - Studio Magic\nVerse: Em - C - G - D\nChorus: C - D - Em - C\n\nRecording notes: Use vintage reverb on vocals",
        "recording_session_notes.docx": "Recording Session Log\n\nBand: The Dream Band\nStudio: Home Studio Setup\nDate: 2024 Sessions\nSongs recorded: 2 tracks\nEquipment: Audio interface, condenser mics\nNext steps: Mix and master both tracks"
    }
    
    for filename, content in files.items():
        filepath = base_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f" Created music project files in {base_dir}")

def create_academic_project():
    """Create academic research project files"""
    base_dir = Path("test_scenarios/scattered_files")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "research_paper_draft.txt": "Title: The Impact of AI on Modern Education\n\nAbstract:\nThis research study examines the transformative effects of artificial intelligence in educational settings. Our analysis covers machine learning applications, student engagement metrics, and learning outcome improvements.\n\nKeywords: artificial intelligence, education, machine learning, student engagement, academic performance\n\nIntroduction:\nArtificial intelligence has emerged as a revolutionary force in education...",
        
        "data_analysis_results.csv": "Student_ID,Pre_AI_Score,Post_AI_Score,Engagement_Level,Course_Type\n001,72,85,High,Mathematics\n002,68,79,Medium,Science\n003,81,92,High,Literature\n004,75,83,High,Mathematics\n005,69,74,Low,Science",
        
        "figure_1_performance_chart.png": "Chart showing student performance improvements with AI integration",
        
        "figure_2_engagement_graph.jpg": "Graph displaying engagement levels across different AI tools",
        
        "bibliography_sources.txt": "References:\n\n1. Johnson, M. (2023). AI in Education: A Comprehensive Review. Journal of Educational Technology, 45(2), 123-145.\n\n2. Smith, R., & Williams, K. (2022). Machine Learning Applications in Student Assessment. Educational Research Quarterly, 38(4), 67-89.\n\n3. Brown, L. (2024). The Future of Personalized Learning. AI Education Review, 12(1), 201-220.",
        
        "conference_presentation.pptx": "AI in Education Research Presentation\nSlide 1: Title - The Impact of AI on Modern Education\nSlide 2: Research Objectives\nSlide 3: Methodology\nSlide 4: Results and Findings\nSlide 5: Conclusions and Future Work",
        
        "final_submission.pdf": "FINAL PAPER: The Impact of AI on Modern Education\n\nThis is the final version submitted to the Journal of Educational Technology.\nIncludes all revisions based on peer review feedback.\nResearch conducted over 12-month period with 500 student participants."
    }
    
    for filename, content in files.items():
        filepath = base_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f" Created academic project files in {base_dir}")

def create_work_project():
    """Create business/work project files"""
    base_dir = Path("test_scenarios/scattered_files")  
    base_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "client_meeting_photo.jpg": "Photo from client presentation meeting",
        
        "project_proposal.docx": "PROJECT PROPOSAL: Website Redesign for TechCorp\n\nClient: TechCorp Industries\nProject: Complete website redesign and development\nTimeline: 8 weeks\nBudget: $25,000\n\nObjectives:\n- Modern, responsive design\n- Improved user experience\n- SEO optimization\n- Mobile-first approach\n\nDeliverables:\n- Wireframes and mockups\n- Frontend development\n- Backend integration\n- Testing and deployment",
        
        "budget_spreadsheet.xlsx": "TechCorp Website Project Budget\nDesign Phase: $8,000\nDevelopment Phase: $12,000\nTesting Phase: $3,000\nProject Management: $2,000\nTotal: $25,000",
        
        "client_presentation.pptx": "TechCorp Website Redesign Presentation\nSlide 1: Project Overview\nSlide 2: Current Site Analysis\nSlide 3: Proposed Design Direction\nSlide 4: Technical Architecture\nSlide 5: Timeline and Milestones\nSlide 6: Budget Breakdown\nSlide 7: Next Steps",
        
        "meeting_notes.md": "# Client Meeting Notes - TechCorp Project\n\n**Date:** March 15, 2024\n**Attendees:** John Smith (TechCorp), Sarah Johnson (Our Team)\n\n## Key Discussion Points:\n- Client wants modern, professional look\n- Must maintain brand colors (blue/white)\n- Need e-commerce functionality\n- Mobile responsiveness critical\n- Launch target: May 1st\n\n## Action Items:\n- [ ] Create initial wireframes\n- [ ] Set up development environment\n- [ ] Schedule design review meeting\n- [ ] Prepare technical specifications",
        
        "contract_signed.pdf": "SERVICE AGREEMENT\nTechCorp Website Redesign Project\nSigned contract between TechCorp Industries and our design agency\nProject start date: March 1, 2024\nExpected completion: April 30, 2024\nTotal project value: $25,000"
    }
    
    for filename, content in files.items():
        filepath = base_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f" Created work project files in {base_dir}")

def create_photo_project():
    """Create vacation/photo project files"""
    base_dir = Path("test_scenarios/scattered_files")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "vacation_sunset.jpg": "Beautiful sunset photo from Hawaii vacation trip",
        "beach_panorama.png": "Panoramic beach view from vacation location", 
        "family_group_photo.jpeg": "Family photo taken during Hawaii vacation",
        "vacation_video_highlights.mp4": "Video compilation of best vacation moments",
        "travel_itinerary.pdf": "Hawaii Vacation Itinerary\nDay 1: Arrival and hotel check-in\nDay 2: Beach day and snorkeling\nDay 3: Volcano tour and hiking\nDay 4: Luau and cultural experiences\nDay 5: Shopping and departure\n\nHotel: Grand Hawaii Resort\nFlight: UA 123 departing 9:30 AM",
        "vacation_journal.txt": "Hawaii Vacation Journal\n\nDay 1: Arrived safely! The hotel is amazing and the ocean view is breathtaking.\nDay 2: Spent the whole day at the beach. The snorkeling was incredible - saw so many colorful fish!\nDay 3: Hiked to the volcano crater. The views were absolutely stunning. Took hundreds of photos.\nDay 4: Traditional luau tonight. Learned about Hawaiian culture and enjoyed amazing food.\nDay 5: Last day - picked up some souvenirs and took final beach photos before heading home."
    }
    
    for filename, content in files.items():
        filepath = base_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f" Created photo/vacation project files in {base_dir}")

def main():
    """Create all test scenarios"""
    print(" Creating realistic test scenarios...")
    print("This will create mixed files that should group into semantic projects\n")
    
    # Create all project types in the same directory (scattered)
    create_music_project()
    create_academic_project() 
    create_work_project()
    create_photo_project()
    
    print(f"\n Test scenarios created!")
    print(f" All files are scattered in: test_scenarios/scattered_files/")
    print(f" Total files: {len(list(Path('test_scenarios/scattered_files').glob('*')))}")
    
    print(f"\n Now test the smart organizer:")
    print(f"   python file_organizer.py --source test_scenarios/scattered_files --dry-run")
    print(f"   python file_organizer.py --source test_scenarios/scattered_files --destination test_scenarios/organized")

if __name__ == "__main__":
    main()
