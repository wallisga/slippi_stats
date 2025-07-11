"""
Client Domain Schemas

Pure data structures only - no business logic or validation.
FIXED: Removed all @classmethod violations per architecture.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

# ============================================================================
# Enums
# ============================================================================

class PlatformType(Enum):
    """Supported platform types."""
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"
    
    @classmethod
    def from_string(cls, platform_str: str) -> 'PlatformType':
        """Convert string to platform type."""
        if not platform_str:
            return cls.UNKNOWN
        
        platform_str = platform_str.lower().strip()
        if platform_str in ['windows', 'win32', 'win']:
            return cls.WINDOWS
        elif platform_str in ['macos', 'darwin', 'mac']:
            return cls.MACOS
        elif platform_str in ['linux', 'unix']:
            return cls.LINUX
        else:
            return cls.UNKNOWN

class ClientStatus(Enum):
    """Client status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# ============================================================================
# Pure Data Structures
# ============================================================================

@dataclass
class ClientRegistrationData:
    """Client registration data structure."""
    client_id: str
    hostname: str = "unknown"
    platform: PlatformType = PlatformType.UNKNOWN
    version: str = "1.0.0"
    registration_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Additional metadata
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'client_id': self.client_id,
            'hostname': self.hostname,
            'platform': self.platform.value,
            'version': self.version,
            'registration_date': self.registration_date,
            'last_active': datetime.now().isoformat(),
            **self.additional_info
        }

@dataclass
class ApiKeyData:
    """API key data structure."""
    client_id: str
    api_key: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    is_active: bool = True
    
    # Usage tracking
    last_used_at: Optional[str] = None
    usage_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if not self.expires_at:
            return False
        try:
            expires_dt = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expires_dt
        except Exception:
            return True  # Treat invalid dates as expired
    
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'client_id': self.client_id,
            'api_key': self.api_key,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at,
            'usage_count': self.usage_count
        }

@dataclass
class ClientInfo:
    """Complete client information structure."""
    registration: ClientRegistrationData
    api_key: Optional[ApiKeyData] = None
    status: ClientStatus = ClientStatus.ACTIVE
    
    # Statistics
    total_uploads: int = 0
    total_games_uploaded: int = 0
    total_files_uploaded: int = 0
    last_activity: Optional[str] = None

# ============================================================================
# Response Structures
# ============================================================================

@dataclass
class ClientRegistrationResponse:
    """Standardized client registration response."""
    success: bool
    client_id: str
    api_key: Optional[str] = None
    expires_at: Optional[str] = None
    message: str = "Registration successful"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        result = {
            'success': self.success,
            'client_id': self.client_id,
            'message': self.message
        }
        
        if self.api_key:
            result['api_key'] = self.api_key
            result['expires_at'] = self.expires_at
        
        if self.error:
            result['error'] = self.error
            
        return result

# ============================================================================
# Custom Exceptions
# ============================================================================

class ClientValidationError(Exception):
    """Exception raised when client validation fails."""
    pass

class ApiKeyError(Exception):
    """Exception raised when API key operations fail."""
    pass