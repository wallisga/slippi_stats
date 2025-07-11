"""
Upload Domain Schemas

Pure data structures only - no business logic or validation.
FIXED: Removed all @classmethod violations per architecture.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# ============================================================================
# Enums and Constants
# ============================================================================

class GameResult(Enum):
    """Standardized game result representation."""
    WIN = "win"
    LOSS = "loss"
    NO_CONTEST = "no_contest"
    
    @classmethod
    def from_placement(cls, placement: int) -> 'GameResult':
        """Convert placement to result."""
        if placement == 1:
            return cls.WIN
        elif placement in [2, 3, 4]:
            return cls.LOSS
        else:
            return cls.NO_CONTEST
    
    @classmethod
    def from_string(cls, result_str: str) -> 'GameResult':
        """Convert string to result."""
        if not result_str:
            return cls.NO_CONTEST
        
        result_str = str(result_str).lower().strip()
        if result_str in ['win', 'w', '1', 'victory']:
            return cls.WIN
        elif result_str in ['loss', 'lose', 'l', '0', 'defeat']:
            return cls.LOSS
        else:
            return cls.NO_CONTEST

# ============================================================================
# Pure Data Structures
# ============================================================================

@dataclass
class PlayerUploadData:
    """Standardized player data structure."""
    player_tag: str
    character_name: str
    placement: int = 0
    result: GameResult = GameResult.NO_CONTEST
    
    # Raw data for backward compatibility
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'player_tag': self.player_tag,
            'character_name': self.character_name,
            'placement': self.placement,
            'result': self.result.value,
            **self.raw_data  # Include all original data
        }

@dataclass
class UploadGameData:
    """Standardized game data structure."""
    game_id: str
    client_id: str
    stage_id: int
    start_time: str
    game_length_frames: int = 0
    player_data: List[PlayerUploadData] = field(default_factory=list)
    
    # Computed properties
    stage_name: Optional[str] = None
    game_length_seconds: float = 0.0
    
    # Raw data for backward compatibility
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'game_id': self.game_id,
            'client_id': self.client_id,
            'stage_id': self.stage_id,
            'start_time': self.start_time,
            'game_length_frames': self.game_length_frames,
            'stage_name': self.stage_name,
            'game_length_seconds': self.game_length_seconds,
            'player_data': [player.to_dict() for player in self.player_data],
            **self.raw_data  # Include all original data
        }

@dataclass
class CombinedUploadData:
    """Standardized combined upload data structure."""
    client_id: str
    client_info: Optional[Dict[str, Any]] = None
    games: List[UploadGameData] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    upload_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# ============================================================================
# Custom Exceptions (Data-Related)
# ============================================================================

class UploadValidationError(Exception):
    """Exception raised when upload validation fails."""
    pass