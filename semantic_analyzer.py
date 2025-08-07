#!/usr/bin/env python3
"""
Semantic Analyzer - Cross-file content similarity detection
Identifies relationships between files to group them into coherent projects.
"""

import os
import asyncio
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import hashlib
import json
from datetime import datetime, timedelta
import re
from collections import defaultdict

# For content similarity
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# File metadata extraction
from mutagen import File as MutagenFile
from PIL import Image
from PIL.ExifTags import TAGS
import docx
import PyPDF2

logger = logging.getLogger(__name__)

@dataclass
class FileSignature:
    """Represents the semantic signature of a file"""
    path: str
    file_type: str
    content_keywords: Set[str]
    metadata: Dict[str, Any]
    created_date: datetime
    modified_date: datetime
    name_tokens: Set[str]
    content_embedding: Optional[np.ndarray] = None

@dataclass
class ProjectCluster:
    """Represents a group of related files forming a project"""
    project_id: str
    project_name: str
    files: List[FileSignature]
    confidence: float
    project_type: str  # "music", "academic", "work", "personal", etc.
    common_keywords: Set[str]
    date_range: Tuple[datetime, datetime]

class SemanticAnalyzer:
    """Analyzes files to detect semantic relationships and project groupings"""
    
    def __init__(self, similarity_threshold: float = 0.3):
        """
        Initialize semantic analyzer.
        
        Args:
            similarity_threshold: Minimum similarity score to consider files related
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )
        self._keyword_cache: Dict[str, Set[str]] = {}
        
    async def analyze_file_signatures(self, file_paths: List[str]) -> List[FileSignature]:
        """
        Extract semantic signatures from all files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            List of FileSignature objects
        """
        signatures = []
        
        for file_path in file_paths:
            try:
                signature = await self._extract_file_signature(file_path)
                if signature:
                    signatures.append(signature)
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
                
        return signatures
    
    async def _extract_file_signature(self, file_path: str) -> Optional[FileSignature]:
        """Extract semantic signature from a single file"""
        if not os.path.exists(file_path):
            return None
            
        path_obj = Path(file_path)
        stats = path_obj.stat()
        
        # Basic file info
        file_type = self._get_file_type(file_path)
        created_date = datetime.fromtimestamp(stats.st_ctime)
        modified_date = datetime.fromtimestamp(stats.st_mtime)
        
        # Extract name tokens
        name_tokens = self._extract_name_tokens(path_obj.stem)
        
        # Extract content keywords based on file type
        content_keywords = await self._extract_content_keywords(file_path, file_type)
        
        # Extract metadata
        metadata = await self._extract_metadata(file_path, file_type)
        
        return FileSignature(
            path=file_path,
            file_type=file_type,
            content_keywords=content_keywords,
            metadata=metadata,
            created_date=created_date,
            modified_date=modified_date,
            name_tokens=name_tokens
        )
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type category"""
        ext = Path(file_path).suffix.lower()
        
        type_mapping = {
            # Documents
            '.pdf': 'document', '.doc': 'document', '.docx': 'document',
            '.txt': 'document', '.md': 'document', '.rtf': 'document',
            
            # Images
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image',
            '.gif': 'image', '.bmp': 'image', '.tiff': 'image',
            
            # Audio
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio',
            '.m4a': 'audio', '.ogg': 'audio', '.aac': 'audio',
            
            # Video
            '.mp4': 'video', '.avi': 'video', '.mov': 'video',
            '.mkv': 'video', '.flv': 'video', '.wmv': 'video',
            
            # Spreadsheets
            '.xls': 'spreadsheet', '.xlsx': 'spreadsheet', '.csv': 'spreadsheet',
            
            # Presentations
            '.ppt': 'presentation', '.pptx': 'presentation',
            
            # Archives
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive'
        }
        
        return type_mapping.get(ext, 'other')
    
    def _extract_name_tokens(self, filename: str) -> Set[str]:
        """Extract meaningful tokens from filename"""
        # Split on common separators and camelCase
        tokens = re.split(r'[-_\s.]+|(?<=[a-z])(?=[A-Z])', filename.lower())
        
        # Filter out short tokens and common words
        stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_tokens = {
            token for token in tokens 
            if len(token) > 2 and token not in stop_words and token.isalpha()
        }
        
        return meaningful_tokens
    
    async def _extract_content_keywords(self, file_path: str, file_type: str) -> Set[str]:
        """Extract keywords from file content based on type"""
        if file_path in self._keyword_cache:
            return self._keyword_cache[file_path]
            
        keywords = set()
        
        try:
            if file_type == 'document':
                keywords = await self._extract_document_keywords(file_path)
            elif file_type == 'audio':
                keywords = await self._extract_audio_keywords(file_path)
            elif file_type == 'image':
                keywords = await self._extract_image_keywords(file_path)
            # Add more extractors as needed
                
        except Exception as e:
            logger.debug(f"Could not extract keywords from {file_path}: {e}")
            
        self._keyword_cache[file_path] = keywords
        return keywords
    
    async def _extract_document_keywords(self, file_path: str) -> Set[str]:
        """Extract keywords from document files"""
        text_content = ""
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.txt' or ext == '.md':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
            elif ext == '.docx':
                doc = docx.Document(file_path)
                text_content = '\n'.join([para.text for para in doc.paragraphs])
            elif ext == '.pdf':
                with open(file_path, 'rb') as f:
                    # Suppress PyPDF2 warnings for better user experience
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore")  # Suppress all PyPDF2 warnings
                        try:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text_content = '\n'.join([
                                page.extract_text() for page in pdf_reader.pages[:5]  # First 5 pages
                            ])
                        except Exception as pdf_error:
                            logger.debug(f"PDF parsing failed for {file_path}: {pdf_error}")
                            # Try to read just the filename for keywords if PDF parsing fails
                            text_content = Path(file_path).stem
        except Exception as e:
            logger.debug(f"Error reading document {file_path}: {e}")
            return set()
        
        # Extract meaningful terms
        if text_content:
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text_content.lower())
            # Get most frequent non-common words
            word_freq = defaultdict(int)
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                         'with', 'by', 'from', 'this', 'that', 'these', 'those', 'are', 'was'}
            
            for word in words:
                if word not in stop_words and len(word) > 3:
                    word_freq[word] += 1
            
            # Return top keywords
            return set([word for word, freq in sorted(word_freq.items(), 
                                                    key=lambda x: x[1], reverse=True)[:20]])
        
        return set()
    
    async def _extract_audio_keywords(self, file_path: str) -> Set[str]:
        """Extract keywords from audio metadata"""
        keywords = set()
        
        try:
            audio_file = MutagenFile(file_path)
            if audio_file:
                # Extract metadata keywords
                for key, value in audio_file.items():
                    if isinstance(value, list):
                        value = ' '.join(str(v) for v in value)
                    elif value:
                        value = str(value)
                        
                    if value:
                        # Split and clean
                        tokens = re.findall(r'\b[a-zA-Z]{2,}\b', value.lower())
                        keywords.update(tokens)
                        
        except Exception as e:
            logger.debug(f"Error reading audio metadata {file_path}: {e}")
            
        return keywords
    
    async def _extract_image_keywords(self, file_path: str) -> Set[str]:
        """Extract keywords from image metadata"""
        keywords = set()
        
        try:
            with Image.open(file_path) as img:
                # Extract EXIF data
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if isinstance(value, str) and len(value) < 100:
                            tokens = re.findall(r'\b[a-zA-Z]{3,}\b', value.lower())
                            keywords.update(tokens)
                            
        except Exception as e:
            logger.debug(f"Error reading image metadata {file_path}: {e}")
            
        return keywords
    
    async def _extract_metadata(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract relevant metadata from file"""
        metadata = {}
        
        try:
            if file_type == 'audio':
                audio_file = MutagenFile(file_path)
                if audio_file:
                    metadata.update({
                        'artist': str(audio_file.get('TPE1', [''])[0] if audio_file.get('TPE1') else ''),
                        'album': str(audio_file.get('TALB', [''])[0] if audio_file.get('TALB') else ''),
                        'title': str(audio_file.get('TIT2', [''])[0] if audio_file.get('TIT2') else ''),
                        'genre': str(audio_file.get('TCON', [''])[0] if audio_file.get('TCON') else ''),
                    })
                    
        except Exception as e:
            logger.debug(f"Error extracting metadata from {file_path}: {e}")
            
        return metadata
    
    def find_project_clusters(self, signatures: List[FileSignature]) -> List[ProjectCluster]:
        """
        Group files into project clusters based on semantic similarity.
        
        Args:
            signatures: List of file signatures to cluster
            
        Returns:
            List of project clusters
        """
        if len(signatures) < 2:
            return []
            
        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(signatures)
        
        # Find clusters using similarity threshold
        clusters = self._cluster_files(signatures, similarity_matrix)
        
        # Convert to ProjectCluster objects
        project_clusters = []
        for i, cluster_files in enumerate(clusters):
            if len(cluster_files) >= 2:  # Only consider clusters with 2+ files
                cluster = self._create_project_cluster(cluster_files, f"project_{i}")
                if cluster:
                    project_clusters.append(cluster)
                    
        return project_clusters
    
    def _calculate_similarity_matrix(self, signatures: List[FileSignature]) -> np.ndarray:
        """Calculate similarity matrix between file signatures"""
        n_files = len(signatures)
        similarity_matrix = np.zeros((n_files, n_files))
        
        for i in range(n_files):
            for j in range(i + 1, n_files):
                similarity = self._calculate_file_similarity(signatures[i], signatures[j])
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
                
        return similarity_matrix
    
    def _calculate_file_similarity(self, sig1: FileSignature, sig2: FileSignature) -> float:
        """Calculate similarity between two file signatures"""
        similarities = []
        
        # Name similarity
        name_sim = len(sig1.name_tokens & sig2.name_tokens) / max(
            len(sig1.name_tokens | sig2.name_tokens), 1
        )
        similarities.append(name_sim * 0.3)
        
        # Content keyword similarity
        content_sim = len(sig1.content_keywords & sig2.content_keywords) / max(
            len(sig1.content_keywords | sig2.content_keywords), 1
        )
        similarities.append(content_sim * 0.4)
        
        # Date proximity (files created/modified around same time)
        time_diff = abs((sig1.created_date - sig2.created_date).total_seconds())
        max_time_diff = 30 * 24 * 3600  # 30 days
        date_sim = max(0, 1 - (time_diff / max_time_diff))
        similarities.append(date_sim * 0.2)
        
        # Metadata similarity (for same file types)
        metadata_sim = 0
        if sig1.file_type == sig2.file_type and sig1.file_type == 'audio':
            # Special handling for audio files
            if (sig1.metadata.get('artist') and sig2.metadata.get('artist') and
                sig1.metadata['artist'] == sig2.metadata['artist']):
                metadata_sim = 0.5
            if (sig1.metadata.get('album') and sig2.metadata.get('album') and
                sig1.metadata['album'] == sig2.metadata['album']):
                metadata_sim = max(metadata_sim, 0.8)
        similarities.append(metadata_sim * 0.1)
        
        return sum(similarities)
    
    def _cluster_files(self, signatures: List[FileSignature], 
                      similarity_matrix: np.ndarray) -> List[List[FileSignature]]:
        """Cluster files based on similarity matrix"""
        n_files = len(signatures)
        visited = [False] * n_files
        clusters = []
        
        for i in range(n_files):
            if visited[i]:
                continue
                
            # Start new cluster
            cluster = [signatures[i]]
            visited[i] = True
            
            # Find similar files
            for j in range(n_files):
                if not visited[j] and similarity_matrix[i][j] >= self.similarity_threshold:
                    cluster.append(signatures[j])
                    visited[j] = True
                    
            clusters.append(cluster)
            
        return clusters
    
    def _create_project_cluster(self, files: List[FileSignature], 
                              project_id: str) -> Optional[ProjectCluster]:
        """Create a ProjectCluster from a group of files"""
        if not files:
            return None
            
        # Find common keywords
        content_keyword_sets = [f.content_keywords for f in files if f.content_keywords]
        if content_keyword_sets:
            common_keywords = set.intersection(*content_keyword_sets)
        else:
            common_keywords = set()
            
        if not common_keywords:
            # If no common content keywords, use name tokens
            name_token_sets = [f.name_tokens for f in files if f.name_tokens]
            if name_token_sets:
                common_keywords = set.intersection(*name_token_sets)
            else:
                common_keywords = set()
            
        # Determine project type based on file types and keywords
        file_types = {f.file_type for f in files}
        project_type = self._determine_project_type(file_types, common_keywords)
        
        # Generate project name
        project_name = self._generate_project_name(files, common_keywords, project_type)
        
        # Calculate confidence based on similarity strength
        confidence = min(1.0, len(common_keywords) / 5.0 + len(files) / 10.0)
        
        # Date range
        dates = [f.created_date for f in files] + [f.modified_date for f in files]
        date_range = (min(dates), max(dates))
        
        return ProjectCluster(
            project_id=project_id,
            project_name=project_name,
            files=files,
            confidence=confidence,
            project_type=project_type,
            common_keywords=common_keywords,
            date_range=date_range
        )
    
    def _determine_project_type(self, file_types: Set[str], keywords: Set[str]) -> str:
        """Determine the type of project based on files and keywords"""
        # Music project indicators
        music_indicators = {'song', 'music', 'band', 'album', 'track', 'recording', 'audio'}
        if 'audio' in file_types and keywords & music_indicators:
            return 'music'
            
        # Academic project indicators  
        academic_indicators = {'research', 'paper', 'study', 'assignment', 'thesis', 'essay', 'report'}
        if 'document' in file_types and keywords & academic_indicators:
            return 'academic'
            
        # Work project indicators
        work_indicators = {'project', 'meeting', 'presentation', 'business', 'client', 'proposal'}
        if keywords & work_indicators:
            return 'work'
            
        # Photo project indicators
        photo_indicators = {'photo', 'picture', 'image', 'vacation', 'trip', 'event'}
        if 'image' in file_types and keywords & photo_indicators:
            return 'photos'
            
        return 'general'
    
    def _generate_project_name(self, files: List[FileSignature], 
                             keywords: Set[str], project_type: str) -> str:
        """Generate a meaningful name for the project"""
        # Use most common keywords
        if keywords:
            primary_keyword = sorted(keywords)[0]  # Take first alphabetically for consistency
            return f"{project_type.title()}_Project_{primary_keyword.title()}"
            
        # Fallback to date-based naming
        dates = [f.created_date for f in files]
        avg_date = min(dates)
        return f"{project_type.title()}_Project_{avg_date.strftime('%Y_%m')}"