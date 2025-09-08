#!/usr/bin/env python3
"""
Smart File Organizer - Main orchestrator for semantic project detection
Implements the innovative cross-format, multi-level organization system.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from semantic_analyzer import SemanticAnalyzer
from nim_integration.embeddings import EmbeddingBackend
from nim_integration.nim_client import NIMClient
from project_detector import ProjectDetector, ProjectStructure
from hierarchy_builder import HierarchyBuilder, OrganizationPlan

logger = logging.getLogger(__name__)

class SmartFileOrganizer:
    """
    Main class that orchestrates the semantic file organization process.
    
    This implements your innovative vision:
    1. Detects semantic relationships between files across different formats
    2. Groups files into meaningful projects (music, academic, work, etc.)
    3. Creates multi-level hierarchies (Project -> Type -> Attributes -> Files)
    4. Organizes by meaning, not just file extension
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.3,
                 base_output_dir: str = "Organized_Files",
                 use_embeddings: bool = True,
                 embedding_backend: Optional[EmbeddingBackend] = None,
                 enable_multimodal: bool = False,
                 vision_model: Optional[str] = None,
                 nim_api_key: Optional[str] = None,
                 nim_base_url: Optional[str] = None):
        """
        Initialize the smart file organizer.
        
        Args:
            similarity_threshold: Minimum similarity to group files into projects
            base_output_dir: Base directory for organized output
            use_embeddings: Whether to use semantic embeddings for improved similarity
        """
        self.semantic_analyzer = SemanticAnalyzer(
            similarity_threshold=similarity_threshold,
            use_embeddings=use_embeddings,
            embedding_backend=embedding_backend,
            enable_multimodal=enable_multimodal,
            vision_model=vision_model,
            nim_api_key=nim_api_key,
            nim_base_url=nim_base_url,
        )
        self.project_detector = ProjectDetector(self.semantic_analyzer)
        self.hierarchy_builder = HierarchyBuilder(base_output_dir)
        
    async def organize_files(self, 
                           source_paths: List[str],
                           destination_dir: Optional[str] = None,
                           dry_run: bool = True) -> Dict[str, Any]:
        """
        Main method to organize files using semantic project detection.
        
        Args:
            source_paths: List of directories/files to organize
            destination_dir: Optional custom destination directory  
            dry_run: If True, only simulate the organization
            
        Returns:
            Dictionary with organization results and statistics
        """
        logger.info("🚀 Starting Smart File Organization")
        logger.info(f"   Source paths: {len(source_paths)}")
        logger.info(f"   Dry run: {dry_run}")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Collect all files from source paths
            logger.info("\n📁 Collecting files...")
            all_files = self._collect_files(source_paths)
            
            if not all_files:
                return {'error': 'No files found to organize'}
                
            logger.info(f"   Found {len(all_files)} files to analyze")
            
            # Step 2: Detect semantic projects
            logger.info("\n🧠 Detecting semantic projects...")
            projects = await self.project_detector.detect_projects(all_files)
            
            if not projects:
                logger.warning("No projects detected - files seem unrelated")
                return {'error': 'No semantic projects detected'}
                
            logger.info(f"   Detected {len(projects)} projects:")
            for project in projects:
                logger.info(f"     • {project.project_name} ({project.file_count} files, "
                           f"confidence: {project.confidence:.2f})")
            
            # Step 3: Create organization plans
            logger.info("\n📋 Creating organization plans...")
            plans = self.hierarchy_builder.create_organization_plans(
                projects, destination_dir
            )
            
            # Step 4: Execute plans
            logger.info(f"\n{'🧪 Simulating' if dry_run else '🎯 Executing'} organization...")
            execution_results = []
            undo_info = self.hierarchy_builder.create_undo_information(plans)
            
            for plan in plans:
                result = self.hierarchy_builder.execute_organization_plan(plan, dry_run)
                execution_results.append(result)
                
                if not dry_run:
                    logger.info(f"   ✅ {plan.project_name}: {result['successful_operations']} files organized")
                else:
                    logger.info(f"   📝 {plan.project_name}: Would organize {result['total_operations']} files")
            
            # Step 5: Generate summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            summary = self._generate_summary(
                projects, plans, execution_results, duration, dry_run
            )
            
            # Save undo information if not dry run
            if not dry_run:
                undo_file = f"undo_info_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
                with open(undo_file, 'w') as f:
                    json.dump(undo_info, f, indent=2)
                summary['undo_file'] = undo_file
                logger.info(f"   💾 Undo information saved to {undo_file}")
            
            logger.info(f"\n🎉 Organization {'simulation' if dry_run else ''} completed!")
            logger.info(f"   Duration: {duration:.2f} seconds")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Organization failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    def _collect_files(self, source_paths: List[str]) -> List[str]:
        """Collect all files from source paths"""
        all_files = []
        
        for source_path in source_paths:
            path_obj = Path(source_path)
            
            if path_obj.is_file():
                all_files.append(str(path_obj))
            elif path_obj.is_dir():
                # Recursively collect files
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        all_files.append(str(file_path))
            else:
                logger.warning(f"Path does not exist: {source_path}")
                
        return all_files
    
    def _generate_summary(self, 
                         projects: List[ProjectStructure],
                         plans: List[OrganizationPlan],
                         results: List[Dict[str, Any]],
                         duration: float,
                         dry_run: bool) -> Dict[str, Any]:
        """Generate comprehensive summary of the organization process"""
        
        total_files = sum(len(plan.source_files) for plan in plans)
        successful_ops = sum(r['successful_operations'] for r in results)
        failed_ops = sum(r['failed_operations'] for r in results)
        total_conflicts = sum(len(plan.conflicts) for plan in plans)
        
        # Project type breakdown
        project_types = {}
        for project in projects:
            project_types[project.project_type] = project_types.get(project.project_type, 0) + 1
        
        # Size distribution
        size_dist = {'small (2-5)': 0, 'medium (6-15)': 0, 'large (16+)': 0}
        for project in projects:
            if project.file_count <= 5:
                size_dist['small (2-5)'] += 1
            elif project.file_count <= 15:
                size_dist['medium (6-15)'] += 1
            else:
                size_dist['large (16+)'] += 1
        
        summary = {
            'operation': 'simulation' if dry_run else 'execution',
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'statistics': {
                'total_projects_detected': len(projects),
                'total_files_processed': total_files,
                'successful_operations': successful_ops,
                'failed_operations': failed_ops,
                'conflicts_detected': total_conflicts,
                'avg_confidence': sum(p.confidence for p in projects) / len(projects) if projects else 0
            },
            'project_breakdown': {
                'by_type': project_types,
                'by_size': size_dist
            },
            'detected_projects': [
                {
                    'name': project.project_name,
                    'type': project.project_type,
                    'file_count': project.file_count,
                    'confidence': round(project.confidence, 2),
                    'structure_preview': self._get_structure_preview(project)
                }
                for project in projects
            ]
        }
        
        return summary
    
    def _get_structure_preview(self, project: ProjectStructure) -> Dict[str, Any]:
        """Get a preview of the project structure"""
        preview = {}
        for folder, contents in project.structure.items():
            if isinstance(contents, list):
                preview[folder] = f"{len(contents)} files"
            elif isinstance(contents, dict):
                subfolder_count = len(contents)
                total_files = sum(
                    len(subcontent) if isinstance(subcontent, list) else 1 
                    for subcontent in contents.values()
                )
                preview[folder] = f"{subfolder_count} subfolders, {total_files} files"
            else:
                preview[folder] = "1 file"
        return preview
    
    async def analyze_files_only(self, source_paths: List[str]) -> Dict[str, Any]:
        """
        Just analyze files without organizing - useful for preview/testing.
        
        Args:
            source_paths: List of directories/files to analyze
            
        Returns:
            Analysis results without organization
        """
        logger.info("🔍 Analyzing files for project detection...")
        
        # Collect files
        all_files = self._collect_files(source_paths)
        if not all_files:
            return {'error': 'No files found'}
            
        # Detect projects
        projects = await self.project_detector.detect_projects(all_files)
        
        if not projects:
            return {'message': 'No semantic projects detected'}
            
        # Return analysis summary
        project_summary = self.project_detector.get_project_summary(projects)
        
        return {
            'analysis_only': True,
            'files_analyzed': len(all_files),
            'projects_detected': len(projects),
            'summary': project_summary,
            'projects': [
                {
                    'name': p.project_name,
                    'type': p.project_type,
                    'files': p.file_count,
                    'confidence': round(p.confidence, 2),
                    'structure': p.structure
                }
                for p in projects
            ]
        }

    async def semantic_search(self, source_paths: List[str], query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Search files semantically using the configured embedding backend.
        """
        files = self._collect_files(source_paths)
        if not files:
            return {'error': 'No files found'}
        # Build signatures (includes embeddings when enabled)
        signatures = await self.semantic_analyzer.analyze_file_signatures(files)
        results = self.semantic_analyzer.rank_by_text_similarity(query, signatures, top_k=top_k)
        return {
            'query': query,
            'results': [{'path': p, 'score': round(float(s), 4)} for p, s in results]
        }

    async def semantic_qa(self, source_paths: List[str], question: str, top_k: int = 8,
                          llm_model: str = "meta/llama3-70b-instruct",
                          api_key: str = None, base_url: str = None) -> Dict[str, Any]:
        """
        Simple retrieval + LLM answer using NIM chat completions.
        """
        files = self._collect_files(source_paths)
        if not files:
            return {'error': 'No files found'}
        signatures = await self.semantic_analyzer.analyze_file_signatures(files)
        ranked = self.semantic_analyzer.rank_by_text_similarity(question, signatures, top_k=top_k)
        context_snippets = []
        for path, _score in ranked:
            try:
                p = Path(path)
                if p.suffix.lower() in {'.txt', '.md'}:
                    context_snippets.append((path, p.read_text(encoding='utf-8', errors='ignore')[:1200]))
                else:
                    context_snippets.append((path, p.stem))
            except Exception:
                context_snippets.append((path, p.stem))
        context_text = "\n\n".join([f"[{Path(p).name}]\n{snippet}" for p, snippet in context_snippets])
        nim = NIMClient(base_url=base_url, api_key=api_key)
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers strictly from the provided context."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer concisely."}
        ]
        resp = nim.chat_completion(llm_model, messages, temperature=0.2)
        answer = resp.get('choices', [{}])[0].get('message', {}).get('content', '')
        return {
            'question': question,
            'answer': answer,
            'top_context': [p for p, _ in ranked]
        }
    
    def undo_organization(self, undo_file: str) -> Dict[str, Any]:
        """
        Undo a previous organization operation.
        
        Args:
            undo_file: Path to the undo information file
            
        Returns:
            Undo operation results
        """
        try:
            with open(undo_file, 'r') as f:
                undo_info = json.load(f)
                
            logger.info(f"🔄 Undoing organization from {undo_info['timestamp']}")
            
            results = self.hierarchy_builder.execute_undo(undo_info)
            
            logger.info(f"✅ Undo completed: {results['successful_operations']} operations reversed")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Undo failed: {e}")
            return {'error': str(e)}


# Convenience function for CLI usage
async def smart_organize_cli(source_dirs: List[str], 
                           destination_dir: Optional[str] = None,
                           dry_run: bool = True,
                           similarity_threshold: float = 0.3) -> Dict[str, Any]:
    """
    CLI-friendly function for smart file organization.
    
    Args:
        source_dirs: List of source directories to organize
        destination_dir: Optional destination directory
        dry_run: Whether to simulate or actually move files
        similarity_threshold: Minimum similarity to group files
        
    Returns:
        Organization results
    """
    organizer = SmartFileOrganizer(
        similarity_threshold=similarity_threshold,
        base_output_dir=destination_dir or "Organized_Files"
    )
    
    return await organizer.organize_files(
        source_paths=source_dirs,
        destination_dir=destination_dir,
        dry_run=dry_run
    )