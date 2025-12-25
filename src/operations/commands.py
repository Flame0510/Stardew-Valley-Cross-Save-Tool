"""Commands - Command Pattern for undoable operations"""

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable

from ..config import Config
from ..strategies import LinkStrategy
from .file_operations import FileOperations


class Command(ABC):
    """Abstract command for operations (Command Pattern)"""
    
    @abstractmethod
    def execute(self) -> 'OperationResult':
        """Execute the command"""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Check if command can be undone"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command"""
        pass


@dataclass
class OperationResult:
    """Result of an operation (Value Object)"""
    success: bool
    message: str
    backup_path: Optional[Path] = None


class MigrateCommand(Command):
    """Command to migrate saves to cloud"""
    
    def __init__(self, game_saves: Path, cloud_saves: Path, logger: Callable[[str], None]):
        self.game_saves = game_saves
        self.cloud_saves = cloud_saves
        self.logger = logger
        self.backup_path: Optional[Path] = None
    
    def execute(self) -> OperationResult:
        try:
            self.logger("[MIGRATE] Starting migration to cloud...")
            FileOperations.ensure_directory(self.cloud_saves)
            FileOperations.copy_contents(self.game_saves, self.cloud_saves, overwrite=True)
            self.logger("[OK] Migration complete! Saves copied to cloud.")
            return OperationResult(
                success=True,
                message="Saves migrated to cloud successfully!"
            )
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def can_undo(self) -> bool:
        return False  # Migrate doesn't need undo (non-destructive)
    
    def undo(self) -> None:
        pass


class LinkCommand(Command):
    """Command to link saves to cloud"""
    
    def __init__(self, game_saves: Path, cloud_saves: Path, link_strategy: LinkStrategy, 
                 config: Config, logger: Callable[[str], None]):
        self.game_saves = game_saves
        self.cloud_saves = cloud_saves
        self.link_strategy = link_strategy
        self.config = config
        self.logger = logger
        self.backup_path: Optional[Path] = None
    
    def execute(self) -> OperationResult:
        try:
            self.logger("[LINK] Starting link setup...")
            
            # Check if already linked
            if self.link_strategy.is_link(self.game_saves):
                return OperationResult(
                    success=False,
                    message="The game Saves folder appears to already be a link/junction. "
                           "Use 'Restore Backup' first."
                )
            
            # Ensure cloud folder exists
            FileOperations.ensure_directory(self.cloud_saves)
            
            # Copy saves to cloud BEFORE removing local
            self.logger("[LINK] Copying saves to cloud folder...")
            FileOperations.copy_contents(self.game_saves, self.cloud_saves, overwrite=True)
            
            # Backup original saves
            self.logger("[LINK] Creating backup...")
            self.backup_path = FileOperations.backup_folder(self.game_saves, self.config.BACKUP_ROOT)
            self.logger(f"[BACKUP] Created: {self.backup_path}")
            
            # Remove original folder
            self.logger("[LINK] Removing original saves folder...")
            FileOperations.remove_path(self.game_saves)
            
            # Create link
            self.logger("[LINK] Creating symlink/junction...")
            self.link_strategy.create_link(self.game_saves, self.cloud_saves)
            
            self.logger("[OK] Link created successfully! Saves are now synced via cloud.")
            return OperationResult(
                success=True,
                message="Link created successfully!",
                backup_path=self.backup_path
            )
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def can_undo(self) -> bool:
        return self.backup_path is not None and self.backup_path.exists()
    
    def undo(self) -> None:
        """Restore from backup"""
        if not self.can_undo():
            raise RuntimeError("No backup available to restore")
        
        # Remove link
        if self.game_saves.exists():
            self.link_strategy.remove_link(self.game_saves)
        
        # Restore backup
        shutil.copytree(self.backup_path, self.game_saves)
        self.logger(f"[UNDO] Restored from backup: {self.backup_path}")


class RestoreCommand(Command):
    """Command to restore from backup"""
    
    def __init__(self, game_saves: Path, backup_path: Optional[Path], 
                 link_strategy: LinkStrategy, logger: Callable[[str], None]):
        self.game_saves = game_saves
        self.backup_path = backup_path
        self.link_strategy = link_strategy
        self.logger = logger
    
    def execute(self) -> OperationResult:
        try:
            if not self.backup_path or not self.backup_path.exists():
                return OperationResult(
                    success=False,
                    message="No backup available. Backup path not set or doesn't exist."
                )
            
            self.logger("[RESTORE] Removing link/junction...")
            if self.game_saves.exists():
                self.link_strategy.remove_link(self.game_saves)
            
            self.logger(f"[RESTORE] Restoring from {self.backup_path}...")
            shutil.copytree(self.backup_path, self.game_saves)
            
            self.logger("[OK] Restore complete!")
            return OperationResult(success=True, message="Backup restored successfully!")
        except Exception as e:
            return OperationResult(success=False, message=str(e))
    
    def can_undo(self) -> bool:
        return False  # Restore itself is an undo operation
    
    def undo(self) -> None:
        pass
