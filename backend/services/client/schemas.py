"""
Client Domain Schemas

Data definitions and structures for client management.
Pure data structures only - no business logic or validation.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

# ============================================================================
# Enums and Constants
# ============================================================================

class ClientStatus(Enum):
    """Client status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class PlatformType(Enum):
    """Platform type enumeration."""
    WINDOWS = "Windows"
    MACOS = "Darwin"
    LINUX = "Linux"
    UNKNOWN = "Unknown"
    
    @classmethod
    def from_string(cls, platform_str: str) -> 'PlatformType':
        """Convert platform string to enum."""
        platform_map = {
            'windows': cls.WINDOWS,
            'win32': cls.WINDOWS,
            'darwin': cls.MACOS,
            'macos': cls.MACOS,
            'linux': cls.LINUX,
            'unix': cls.LINUX
        }
        return platform_map.get(platform_str.lower(), cls.UNKNOWN)

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class ClientRegistrationData:
    """Standardized client registration data structure."""
    client_id: str
    hostname: str = "unknown"
    platform: PlatformType = PlatformType.UNKNOWN
    version: str = "1.0.0"
    registration_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Additional metadata
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_registration_request(cls, raw_data: Dict[str, Any]) -> 'ClientRegistrationData':
        """Create from raw registration request data."""
        client_id = raw_data.get('client_id')
        if not client_id:
            client_id = str(uuid.uuid4())
        
        platform_str = raw_data.get('platform', 'unknown')
        platform = PlatformType.from_string(platform_str)
        
        return cls(
            client_id=client_id,
            hostname=raw_data.get('hostname', 'unknown'),
            platform=platform,
            version=raw_data.get('version', '1.0.0'),
            registration_date=raw_data.get('registration_date', datetime.now().isoformat()),
            user_agent=raw_data.get('user_agent'),
            ip_address=raw_data.get('ip_address'),
            additional_info={k: v for k, v in raw_data.items() 
                           if k not in ['client_id', 'hostname', 'platform', 'version', 'registration_date']}
        )
    
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
    """Standardized API key data structure."""
    client_id: str
    api_key: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    is_active: bool = True
    
    # Usage tracking
    last_used_at: Optional[str] = None
    usage_count: int = 0
    
    @classmethod
    def create_new(cls, client_id: str, expiry_days: int = 365) -> 'ApiKeyData':
        """Create a new API key with expiration."""
        import secrets
        import hashlib
        
        # Generate secure API key
        current_time = datetime.now().isoformat()
        random_bytes = secrets.token_bytes(32)
        api_key = hashlib.sha256(f"{client_id}:{current_time}:{random_bytes.hex()}".encode()).hexdigest()
        
        # Calculate expiration
        expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        return cls(
            client_id=client_id,
            api_key=api_key,
            created_at=current_time,
            expires_at=expires_at,
            is_active=True
        )
    
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
    
    @classmethod
    def from_database_records(cls, client_record: Dict[str, Any], 
                            api_key_record: Optional[Dict[str, Any]] = None) -> 'ClientInfo':
        """Create from database records."""
        # Create registration data
        registration = ClientRegistrationData(
            client_id=client_record['client_id'],
            hostname=client_record.get('hostname', 'unknown'),
            platform=PlatformType.from_string(client_record.get('platform', 'unknown')),
            version=client_record.get('version', '1.0.0'),
            registration_date=client_record.get('registration_date', datetime.now().isoformat())
        )
        
        # Create API key data if available
        api_key = None
        if api_key_record:
            api_key = ApiKeyData(
                client_id=api_key_record['client_id'],
                api_key=api_key_record['api_key'],
                created_at=api_key_record.get('created_at', datetime.now().isoformat()),
                expires_at=api_key_record.get('expires_at'),
                is_active=api_key_record.get('is_active', True),
                last_used_at=api_key_record.get('last_used_at'),
                usage_count=api_key_record.get('usage_count', 0)
            )
        
        return cls(
            registration=registration,
            api_key=api_key,
            status=ClientStatus(client_record.get('status', 'active')),
            total_uploads=client_record.get('total_uploads', 0),
            total_games_uploaded=client_record.get('total_games_uploaded', 0),
            total_files_uploaded=client_record.get('total_files_uploaded', 0),
            last_activity=client_record.get('last_active')
        )

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