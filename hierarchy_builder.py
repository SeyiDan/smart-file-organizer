#!/usr/bin/env python3
"""
Hierarchy Builder - Creates dynamic multi-level folder structures
Implements the progressive classification system for project organization.
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

from project_detector import ProjectStructure

logger = logging.getLogger(__name__)

@dataclass
class OrganizationPlan:
    """Represents a plan for organizing files"""
    project_name: str
    source_files: List[str]
    target_structure: Dict[str, Any]
    base_destination: str
    operations: List[Dict[str, str]]  # List of file operations
    conflicts: List[Dict[str, Any]]   # List of potential conflicts

class HierarchyBuilder:
    """Builds and manages dynamic folder hierarchies for project organization"""
    
    def __init__(self, base_output_dir: str = "Organized_Files"):
        """
        Initialize hierarchy builder.
        
        Args:
            base_output_dir: Base directory for organized files
        """
        self.base_output_dir = Path(base_output_dir)
        self.operation_log: List[Dict[str, Any]] = []
        
    def create_organization_plans(self, projects: List[ProjectStructure],
                                destination_dir: Optional[str] = None) -> List[OrganizationPlan]:
        """
        Create organization plans for detected projects.
        
        Args:
            projects: List of detected project structures
            destination_dir: Optional custom destination directory
            
        Returns:
            List of organization plans
        """
        if destination_dir:
            self.base_output_dir = Path(destination_dir)
            
        plans = []
        
        for project in projects:
            plan = self._create_project_plan(project)
            if plan:
                plans.append(plan)
                
        return plans
    
    def _create_project_plan(self, project: ProjectStructure) -> Optional[OrganizationPlan]:
        """Create organization plan for a single project"""
        # Determine project destination
        project_base = self.base_output_dir / self._sanitize_name(project.project_name)
        
        # Collect all source files
        source_files = []
        operations = []
        conflicts = []
        
        # Process the project structure
        for folder_name, contents in project.structure.items():
            self._process_structure_level(
                contents, 
                project_base / folder_name,
                source_files,
                operations,
                conflicts
            )
        
        return OrganizationPlan(
            project_name=project.project_name,
            source_files=source_files,
            target_structure=project.structure,
            base_destination=str(project_base),
            operations=operations,
            conflicts=conflicts
        )
    
    def _process_structure_level(self, contents: Any, current_path: Path,
                               source_files: List[str], operations: List[Dict[str, str]],
                               conflicts: List[Dict[str, Any]]):
        """Recursively process structure levels to create operations"""
        if isinstance(contents, list):
            # List of file paths
            for file_path in contents:
                if os.path.exists(file_path):
                    source_files.append(file_path)
                    target_file = current_path / Path(file_path).name
                    
                    # Check for conflicts
                    if target_file.exists():
                        conflicts.append({
                            'source': file_path,
                            'target': str(target_file),
                            'conflict_type': 'file_exists',
                            'resolution': 'rename'
                        })
                        # Rename target
                        target_file = self._get_unique_filename(target_file)
                    
                    operations.append({
                        'operation': 'move',
                        'source': file_path,
                        'target': str(target_file)
                    })
                    
        elif isinstance(contents, dict):
            # Nested structure
            for subfolder, subcontent in contents.items():
                subfolder_path = current_path / self._sanitize_name(subfolder)
                self._process_structure_level(
                    subcontent, subfolder_path, source_files, operations, conflicts
                )
    
    def execute_organization_plan(self, plan: OrganizationPlan, 
                                dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute an organization plan.
        
        Args:
            plan: Organization plan to execute
            dry_run: If True, only simulate the operations
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"{'Simulating' if dry_run else 'Executing'} organization plan: {plan.project_name}")
        
        execution_start = datetime.now()
        results = {
            'project_name': plan.project_name,
            'total_operations': len(plan.operations),
            'successful_operations': 0,
            'failed_operations': 0,
            'conflicts_resolved': 0,
            'errors': [],
            'dry_run': dry_run
        }
        
        if not dry_run:
            # Create base directory
            try:
                os.makedirs(plan.base_destination, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create base directory {plan.base_destination}: {e}")
                results['errors'].append(f"Failed to create base directory: {e}")
                return results
        
        # Execute operations
        for operation in plan.operations:
            try:
                success = self._execute_operation(operation, dry_run)
                if success:
                    results['successful_operations'] += 1
                else:
                    results['failed_operations'] += 1
                    
            except Exception as e:
                logger.error(f"Operation failed: {operation}, error: {e}")
                results['failed_operations'] += 1
                results['errors'].append(f"Operation {operation['operation']}: {e}")
        
        # Handle conflicts
        results['conflicts_resolved'] = len(plan.conflicts)
        
        # Log the session
        execution_end = datetime.now()
        duration = (execution_end - execution_start).total_seconds()
        
        session_log = {
            'timestamp': execution_start.isoformat(),
            'plan': plan.project_name,
            'duration_seconds': duration,
            'results': results
        }
        
        self.operation_log.append(session_log)
        
        if not dry_run:
            logger.info(f"Organization completed: {results['successful_operations']} successful, "
                       f"{results['failed_operations']} failed operations")
        
        return results
    
    def _execute_operation(self, operation: Dict[str, str], dry_run: bool) -> bool:
        """Execute a single file operation"""
        op_type = operation['operation']
        source = operation['source']
        target = operation['target']
        
        if dry_run:
            logger.debug(f"Would {op_type}: {source} -> {target}")
            return True
        
        try:
            # Ensure target directory exists
            target_dir = Path(target).parent
            os.makedirs(target_dir, exist_ok=True)
            
            if op_type == 'move':
                shutil.move(source, target)
                logger.debug(f"Moved: {source} -> {target}")
            elif op_type == 'copy':
                shutil.copy2(source, target)
                logger.debug(f"Copied: {source} -> {target}")
            else:
                logger.warning(f"Unknown operation type: {op_type}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to {op_type} {source} to {target}: {e}")
            return False
    
    def _get_unique_filename(self, filepath: Path) -> Path:
        """Generate unique filename to avoid conflicts"""
        base = filepath.stem
        suffix = filepath.suffix
        parent = filepath.parent
        counter = 1
        
        while True:
            new_name = f"{base}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for filesystem use"""
        import re
        # Replace invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Remove leading/trailing underscores and spaces
        safe_name = safe_name.strip('_ ')
        # Limit length
        if len(safe_name) > 100:
            safe_name = safe_name[:100].rstrip('_')
        # Ensure not empty
        if not safe_name:
            safe_name = 'Unnamed'
            
        return safe_name
    
    def create_undo_information(self, plans: List[OrganizationPlan]) -> Dict[str, Any]:
        """Create information needed to undo organization operations"""
        undo_info = {
            'timestamp': datetime.now().isoformat(),
            'operations': [],
            'created_directories': []
        }
        
        for plan in plans:
            # Store reverse operations for undo
            for operation in plan.operations:
                if operation['operation'] == 'move':
                    undo_info['operations'].append({
                        'operation': 'move',
                        'source': operation['target'],  # Reverse
                        'target': operation['source']   # Reverse
                    })
            
            # Store created directories
            undo_info['created_directories'].append(plan.base_destination)
        
        return undo_info
    
    def execute_undo(self, undo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute undo operations to reverse organization"""
        logger.info("Executing undo operations...")
        
        results = {
            'successful_operations': 0,
            'failed_operations': 0,
            'errors': []
        }
        
        # Reverse the operations (in reverse order)
        for operation in reversed(undo_info['operations']):
            try:
                success = self._execute_operation(operation, dry_run=False)
                if success:
                    results['successful_operations'] += 1
                else:
                    results['failed_operations'] += 1
            except Exception as e:
                results['failed_operations'] += 1
                results['errors'].append(f"Undo operation failed: {e}")
        
        # Clean up empty directories
        for directory in undo_info['created_directories']:
            try:
                if os.path.exists(directory) and not os.listdir(directory):
                    os.rmdir(directory)
                    logger.info(f"Removed empty directory: {directory}")
            except Exception as e:
                logger.warning(f"Could not remove directory {directory}: {e}")
        
        logger.info(f"Undo completed: {results['successful_operations']} successful, "
                   f"{results['failed_operations']} failed operations")
        
        return results
    
    def get_organization_summary(self, plans: List[OrganizationPlan]) -> Dict[str, Any]:
        """Generate summary of organization plans"""
        if not plans:
            return {}
        
        total_files = sum(len(plan.source_files) for plan in plans)
        total_conflicts = sum(len(plan.conflicts) for plan in plans)
        
        summary = {
            'total_projects': len(plans),
            'total_files': total_files,
            'total_conflicts': total_conflicts,
            'projects': [
                {
                    'name': plan.project_name,
                    'file_count': len(plan.source_files),
                    'conflicts': len(plan.conflicts),
                    'destination': plan.base_destination
                }
                for plan in plans
            ]
        }
        
        return summary
    
    def save_organization_log(self, filepath: str = "organization_log.json"):
        """Save operation log to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.operation_log, f, indent=2)
            logger.info(f"Organization log saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save log: {e}")