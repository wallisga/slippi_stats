"""
Upload Domain Schemas

Pure data structure definitions. No validation logic.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
from datetime import datetime
import uuid

# ============================================================================
# Enums and Constants (Data Definitions)
# ============================================================================

class GameResult(Enum):
    WIN = "Win"
    LOSS = "Loss"
    
    @classmethod
    def from_placement(cls, placement: Union[int, str]) -> 'GameResult':
        try:
            placement_int = int(placement)
            return cls.WIN if placement_int == 1 else cls.LOSS
        except (ValueError, TypeError):
            return cls.LOSS
    
    @classmethod  
    def from_result_string(cls, result: Union[str, None]) -> 'GameResult':
        if not result:
            return cls.LOSS
        result_str = str(result).lower().strip()
        if result_str in ['win', 'winner', '1', 'true']:
            return cls.WIN
        return cls.LOSS

# Character and stage mappings
CHARACTER_MAP = {
    'Fox': 20, 'Falco': 21, 'Marth': 22, 'Sheik': 23,
    # ... etc
}

STAGE_MAP = {
    28: 'Dream Land', 31: 'Battlefield', 32: 'Final Destination',
    # ... etc
}

# ============================================================================
# Data Schema Classes (Pure Data Structures)
# ============================================================================

@dataclass
class UploadPlayerData:
    """Player data within a game upload."""
    player_tag: str
    character_name: str
    character_id: int
    result: GameResult
    placement: int
    stocks_remaining: Optional[int] = None
    damage_dealt: Optional[float] = None
    damage_taken: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['result'] = self.result.value
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_upload_data(cls, raw_player: Dict[str, Any], default_placement: int = 1) -> 'UploadPlayerData':
        """Create from raw upload data."""
        player_tag = str(raw_player.get('player_tag', '')).strip()
        character_name = str(raw_player.get('character_name', 'Unknown')).strip()
        character_id = CHARACTER_MAP.get(character_name, 0)
        
        # Extract result using helper method
        result = cls._extract_standardized_result(raw_player, default_placement)
        placement = raw_player.get('placement', default_placement)
        
        return cls(
            player_tag=player_tag,
            character_name=character_name,
            character_id=character_id,
            result=result,
            placement=placement,
            stocks_remaining=raw_player.get('stocks_remaining'),
            damage_dealt=raw_player.get('damage_dealt'),
            damage_taken=raw_player.get('damage_taken')
        )
    
    @staticmethod
    def _extract_standardized_result(raw_player: Dict[str, Any], default_placement: int) -> GameResult:
        """Extract standardized result from various formats."""
        if 'result' in raw_player and raw_player['result']:
            return GameResult.from_result_string(raw_player['result'])
        if 'placement' in raw_player:
            return GameResult.from_placement(raw_player['placement'])
        return GameResult.from_placement(default_placement)

@dataclass
class UploadGameData:
    """Complete game data for upload processing."""
    game_id: str
    client_id: str
    start_time: str
    stage_id: int
    stage_name: str
    game_length_frames: int
    game_length_seconds: float
    game_type: str = "versus"
    players: List[UploadPlayerData] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    upload_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def player_count(self) -> int:
        return len(self.players)
    
    def get_player(self, player_tag: str) -> Optional[UploadPlayerData]:
        player_tag_lower = player_tag.lower()
        for player in self.players:
            if player.player_tag.lower() == player_tag_lower:
                return player
        return None
    
    def to_database_format(self) -> Dict[str, Any]:
        """Convert to database storage format."""
        return {
            'game_id': self.game_id,
            'client_id': self.client_id,
            'start_time': self.start_time,
            'stage_id': self.stage_id,
            'game_length_frames': self.game_length_frames,
            'game_type': self.game_type,
            'player_data': json.dumps([p.to_dict() for p in self.players]),
            'full_data': json.dumps({
                'game_id': self.game_id,
                'start_time': self.start_time,
                'stage_id': self.stage_id,
                'stage_name': self.stage_name,
                'game_length_frames': self.game_length_frames,
                'game_length_seconds': self.game_length_seconds,
                'game_type': self.game_type,
                'player_data': [p.to_dict() for p in self.players],
                'metadata': self.metadata
            })
        }
    
    @classmethod
    def from_upload_data(cls, raw_game: Dict[str, Any], client_id: str) -> 'UploadGameData':
        """Create from raw client upload data."""
        game_id = str(raw_game.get('game_id', '')).strip()
        if not game_id:
            game_id = str(uuid.uuid4())
        
        start_time = raw_game.get('start_time', datetime.now().isoformat())
        stage_id = int(raw_game.get('stage_id', 0))
        frames = int(raw_game.get('game_length_frames', 0))
        game_type = str(raw_game.get('game_type', 'versus')).strip()
        
        # Compute display fields
        stage_name = STAGE_MAP.get(stage_id, f'Stage {stage_id}')
        game_length_seconds = frames / 60.0 if frames > 0 else 0.0
        
        # Process players
        players = []
        raw_players = raw_game.get('player_data', [])
        for i, raw_player in enumerate(raw_players):
            player = UploadPlayerData.from_upload_data(raw_player, i + 1)
            players.append(player)
        
        return cls(
            game_id=game_id,
            client_id=client_id,
            start_time=start_time,
            stage_id=stage_id,
            stage_name=stage_name,
            game_length_frames=frames,
            game_length_seconds=game_length_seconds,
            game_type=game_type,
            players=players,
            metadata=raw_game.get('metadata', {})
        )

@dataclass
class CombinedUploadData:
    """Combined upload payload schema."""
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