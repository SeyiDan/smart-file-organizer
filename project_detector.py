#!/usr/bin/env python3
"""
Project Detector - Advanced project relationship detection
Builds on semantic analysis to create intelligent project groupings.
"""

import os
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
from pathlib import Path as _Path
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

from semantic_analyzer import SemanticAnalyzer, FileSignature, ProjectCluster

logger = logging.getLogger(__name__)

@dataclass
class ProjectStructure:
    """Represents the hierarchical structure of a detected project"""
    project_name: str
    base_path: str
    structure: Dict[str, Any]  # Nested dict representing folder hierarchy
    confidence: float
    file_count: int
    project_type: str

class ProjectDetector:
    """Detects and structures projects from file clusters"""
    
    def __init__(self, semantic_analyzer: Optional[SemanticAnalyzer] = None):
        """Initialize project detector"""
        self.semantic_analyzer = semantic_analyzer or SemanticAnalyzer()
        
    async def detect_projects(self, file_paths: List[str]) -> List[ProjectStructure]:
        """
        Detect projects from a list of file paths.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of detected project structures
        """
        # Step 1: Extract file signatures
        logger.info(f"Analyzing {len(file_paths)} files for project detection...")
        signatures = await self.semantic_analyzer.analyze_file_signatures(file_paths)
        
        if not signatures:
            logger.warning("No valid file signatures extracted")
            return []
            
        # Step 2: Find project clusters
        logger.info("Detecting project clusters...")
        clusters = self.semantic_analyzer.find_project_clusters(signatures)
        
        if not clusters:
            logger.info("No project clusters detected")
            return []
            
        # Step 3: Create project structures
        logger.info(f"Creating structures for {len(clusters)} detected projects...")
        project_structures = []
        
        for cluster in clusters:
            structure = self._create_project_structure(cluster)
            if structure:
                project_structures.append(structure)
                
        return project_structures
    
    def _create_project_structure(self, cluster: ProjectCluster) -> Optional[ProjectStructure]:
        """Create a hierarchical project structure from a cluster"""
        if not cluster.files:
            return None
            
        # Group files by type for initial organization
        files_by_type = defaultdict(list)
        for file_sig in cluster.files:
            files_by_type[file_sig.file_type].append(file_sig)
            
        # Create the project structure
        structure = {}
        
        # Level 1: File type categories
        for file_type, files in files_by_type.items():
            type_folder = self._get_type_folder_name(file_type, cluster.project_type)
            
            if len(files) == 1:
                # Single file - place directly in type folder
                structure[type_folder] = [files[0].path]
            else:
                # Multiple files - create subcategories
                subcategories = self._create_subcategories(files, cluster.project_type)
                structure[type_folder] = subcategories
                
        return ProjectStructure(
            project_name=cluster.project_name,
            base_path="",  # Will be set when creating actual folders
            structure=structure,
            confidence=cluster.confidence,
            file_count=len(cluster.files),
            project_type=cluster.project_type
        )
    
    def _get_type_folder_name(self, file_type: str, project_type: str) -> str:
        """Get appropriate folder name for file type within project context"""
        type_mapping = {
            'audio': 'Audio',
            'image': 'Images', 
            'video': 'Videos',
            'document': 'Documents',
            'spreadsheet': 'Spreadsheets',
            'presentation': 'Presentations',
            'archive': 'Archives'
        }
        
        base_name = type_mapping.get(file_type, file_type.title())
        
        # Context-specific naming
        if project_type == 'music':
            if file_type == 'audio':
                return 'Songs'
            elif file_type == 'image':
                return 'Album_Art'
            elif file_type == 'document':
                return 'Lyrics_Notes'
        elif project_type == 'academic':
            if file_type == 'document':
                return 'Papers_Documents' 
            elif file_type == 'image':
                return 'Figures_Images'
        elif project_type == 'photos':
            if file_type == 'image':
                return 'Photos'
            elif file_type == 'video':
                return 'Videos'
                
        return base_name
    
    def _create_subcategories(self, files: List[FileSignature], 
                            project_type: str) -> Dict[str, List[str]]:
        """Create subcategories within a file type based on content/metadata"""
        if not files:
            return {}
        
        # Respect minimum size before creating subfolders: place files directly if small
        min_size = self._min_files_for_subfolder()
        if len(files) < min_size:
            return [f.path for f in files]  # Return list to avoid extra folder nesting
            
        # Special handling for different project types
        if project_type == 'music' and files[0].file_type == 'audio':
            sub = self._create_audio_subcategories(files)
        elif project_type == 'academic' and files[0].file_type == 'document':
            sub = self._create_document_subcategories(files)
        elif project_type == 'photos' and files[0].file_type == 'image':
            sub = self._create_image_subcategories(files)
        else:
            sub = self._create_generic_subcategories(files)

        # If each subcategory contains only one file, avoid deep folders: flatten
        try:
            if isinstance(sub, dict):
                lists = list(sub.values())
                if lists and all(isinstance(v, list) and len(v) == 1 for v in lists):
                    return [v[0] for v in lists]
        except Exception:
            pass

        return sub
    
    def _create_audio_subcategories(self, files: List[FileSignature]) -> Dict[str, List[str]]:
        """Create subcategories for audio files"""
        subcategories = defaultdict(list)
        
        # Group by artist if available
        artists = defaultdict(list)
        for file_sig in files:
            artist = file_sig.metadata.get('artist', '').strip()
            if artist:
                artists[artist].append(file_sig.path)
            else:
                artists['Unknown_Artist'].append(file_sig.path)
                
        # If multiple artists, use artist-based subcategories
        if len(artists) > 1:
            for artist, paths in artists.items():
                safe_artist = self._sanitize_folder_name(artist)
                subcategories[f"By_Artist/{safe_artist}"] = paths
        else:
            # Single artist or unknown - group by album or date
            albums = defaultdict(list)
            for file_sig in files:
                album = file_sig.metadata.get('album', '').strip()
                if album:
                    albums[album].append(file_sig.path)
                else:
                    # Group by creation date
                    date_key = file_sig.created_date.strftime('%Y_%m')
                    albums[f"Created_{date_key}"].append(file_sig.path)
                    
            for album, paths in albums.items():
                safe_album = self._sanitize_folder_name(album)
                subcategories[safe_album] = paths
                
        return dict(subcategories)
    
    def _create_document_subcategories(self, files: List[FileSignature]) -> Dict[str, List[str]]:
        """Create subcategories for document files"""
        subcategories = defaultdict(list)
        
        # Analyze content keywords to determine document types
        for file_sig in files:
            category = self._classify_document_type(file_sig)
            subcategories[category].append(file_sig.path)
            
        return dict(subcategories)
    
    def _classify_document_type(self, file_sig: FileSignature) -> str:
        """Classify document based on content and name"""
        keywords = file_sig.content_keywords | file_sig.name_tokens
        
        # Check for specific document types
        if any(word in keywords for word in ['draft', 'rough', 'outline']):
            return 'Drafts'
        elif any(word in keywords for word in ['final', 'submission', 'complete']):
            return 'Final_Documents'
        elif any(word in keywords for word in ['research', 'source', 'reference']):
            return 'Research_Materials'
        elif any(word in keywords for word in ['note', 'notes', 'memo']):
            return 'Notes'
        elif any(word in keywords for word in ['report', 'analysis', 'summary']):
            return 'Reports'
        else:
            return 'Documents'
    
    def _create_image_subcategories(self, files: List[FileSignature]) -> Dict[str, List[str]]:
        """Create subcategories for image files"""
        subcategories = defaultdict(list)
        
        # Group by creation date or content type
        for file_sig in files:
            keywords = file_sig.content_keywords | file_sig.name_tokens
            
            if any(word in keywords for word in ['screenshot', 'screen', 'capture']):
                subcategories['Screenshots'].append(file_sig.path)
            elif any(word in keywords for word in ['photo', 'pic', 'picture']):
                # Group photos by date
                date_key = file_sig.created_date.strftime('%Y_%m_%d')
                subcategories[f'Photos_{date_key}'].append(file_sig.path)
            elif any(word in keywords for word in ['art', 'design', 'graphic']):
                subcategories['Graphics'].append(file_sig.path)
            else:
                subcategories['Images'].append(file_sig.path)
                
        return dict(subcategories)
    
    def _create_generic_subcategories(self, files: List[FileSignature]) -> Dict[str, List[str]]:
        """Create generic subcategories based on common patterns"""
        subcategories = defaultdict(list)
        
        # Group by common keywords or creation time
        if len(files) <= 3:
            # Few files - keep them together
            subcategories['Files'] = [f.path for f in files]
        else:
            # Many files - group by date
            for file_sig in files:
                date_key = file_sig.created_date.strftime('%Y_%m')
                subcategories[f'Created_{date_key}'].append(file_sig.path)
                
        return dict(subcategories)
    
    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize a string to be safe for folder names"""
        # Replace invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        # Limit length
        if len(safe_name) > 50:
            safe_name = safe_name[:50].rstrip('_')
        # Ensure not empty
        if not safe_name:
            safe_name = 'Untitled'
            
        return safe_name

    def _min_files_for_subfolder(self) -> int:
        """Load minimum files required to create a subfolder from config.yaml; default to 3."""
        default_val = 3
        try:
            if yaml is not None:
                cfg_path = _Path.cwd() / 'config.yaml'
                if cfg_path.exists():
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        cfg = yaml.safe_load(f) or {}
                    org = (cfg.get('organization', {}) or {})
                    val = int(org.get('min_files_for_subfolder', default_val))
                    return val if val > 1 else default_val
        except Exception:
            pass
        return default_val
    
    def get_project_summary(self, projects: List[ProjectStructure]) -> Dict[str, Any]:
        """Generate summary statistics for detected projects"""
        if not projects:
            return {}
            
        summary = {
            'total_projects': len(projects),
            'total_files': sum(p.file_count for p in projects),
            'project_types': Counter(p.project_type for p in projects),
            'avg_confidence': sum(p.confidence for p in projects) / len(projects),
            'projects_by_size': {
                'small (2-5 files)': len([p for p in projects if p.file_count <= 5]),
                'medium (6-15 files)': len([p for p in projects if 6 <= p.file_count <= 15]),
                'large (16+ files)': len([p for p in projects if p.file_count > 15])
            }
        }
        
        return summary