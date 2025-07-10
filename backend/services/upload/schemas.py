"""
Upload Domain Schemas

Data definitions and structures for upload processing.
Pure data structures only - no business logic or validation.
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
# Data Structures
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
    
    @classmethod
    def from_upload_data(cls, raw_player: Dict[str, Any]) -> 'PlayerUploadData':
        """Create from raw upload data."""
        player_tag = raw_player.get('player_tag', '')
        character_name = raw_player.get('character_name', 'Unknown')
        placement = int(raw_player.get('placement', 0))
        
        # Determine result from multiple possible fields
        result = GameResult.NO_CONTEST
        if 'result' in raw_player:
            result = GameResult.from_string(raw_player['result'])
        elif placement > 0:
            result = GameResult.from_placement(placement)
        
        return cls(
            player_tag=player_tag,
            character_name=character_name,
            placement=placement,
            result=result,
            raw_data=raw_player
        )
    
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
    
    @classmethod
    def from_upload_data(cls, raw_game: Dict[str, Any], client_id: str) -> 'UploadGameData':
        """Create from raw upload data."""
        # Generate game ID if not provided
        game_id = raw_game.get('game_id', str(uuid.uuid4()))
        
        # Extract basic fields
        stage_id = int(raw_game.get('stage_id', 0))
        start_time = raw_game.get('start_time', datetime.now().isoformat())
        game_length_frames = int(raw_game.get('game_length_frames', 0))
        
        # Process player data
        player_data = []
        for raw_player in raw_game.get('player_data', []):
            player = PlayerUploadData.from_upload_data(raw_player)
            player_data.append(player)
        
        # Compute derived fields
        stage_name = _get_stage_name(stage_id)
        game_length_seconds = game_length_frames / 60.0 if game_length_frames > 0 else 0.0
        
        return cls(
            game_id=game_id,
            client_id=client_id,
            stage_id=stage_id,
            start_time=start_time,
            game_length_frames=game_length_frames,
            player_data=player_data,
            stage_name=stage_name,
            game_length_seconds=game_length_seconds,
            raw_data=raw_game
        )
    
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
    
    @classmethod
    def from_upload_request(cls, client_id: str, raw_upload: Dict[str, Any]) -> 'CombinedUploadData':
        """Create from raw upload request."""
        import logging
        logger = logging.getLogger(__name__)
        
        games = []
        for raw_game in raw_upload.get('games', []):
            try:
                game_data = UploadGameData.from_upload_data(raw_game, client_id)
                games.append(game_data)
            except Exception as e:
                logger.warning(f"Skipping invalid game data: {str(e)}")
        
        return cls(
            client_id=client_id,
            client_info=raw_upload.get('client_info'),
            games=games,
            files=raw_upload.get('files', []),
            metadata=raw_upload.get('metadata', {})
        )

# ============================================================================
# Custom Exceptions (Data-Related)
# ============================================================================

class UploadValidationError(Exception):
    """Exception raised when upload validation fails."""
    pass

# ============================================================================
# Helper Functions (Data Processing Only)
# ============================================================================

def _get_stage_name(stage_id: int) -> Optional[str]:
    """Get stage name from stage ID."""
    # Stage ID to name mapping
    stage_names = {
        2: "Fountain of Dreams",
        3: "Pokemon Stadium",
        8: "Yoshi's Story",
        28: "Dream Land N64",
        31: "Battlefield",
        32: "Final Destination"
    }
    return stage_names.get(stage_id, f"Unknown Stage ({stage_id})")