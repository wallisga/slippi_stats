"""
Client Domain Validation Logic

Input validation and business rules for client operations.
Contains all validation functions and business rule enforcement.
"""

import logging
import re
from typing import Dict, Any
from .schemas import ClientRegistrationData, ClientValidationError, ApiKeyError

logger = logging.getLogger(__name__)

# ============================================================================
# Client Registration Validation
# ============================================================================

def validate_client_registration(raw_data: Dict[str, Any], registration_key: str = None) -> ClientRegistrationData:
    """
    Validate client registration data and return standardized structure.
    
    Args:
        raw_data: Raw registration data from request
        registration_key: Optional registration key for validation
    
    Returns:
        ClientRegistrationData: Validated and standardized registration data
        
    Raises:
        ClientValidationError: If validation fails
    """
    # Validate basic structure
    if not raw_data or not isinstance(raw_data, dict):
        raise ClientValidationError("Registration data must be a non-empty dictionary")
    
    # Validate registration key if required
    if registration_key is not None:
        validate_registration_key(registration_key)
    
    # Validate business rules
    validate_client_registration_business_rules(raw_data)
    
    # Convert to standardized format
    try:
        registration_data = ClientRegistrationData.from_registration_request(raw_data)
    except Exception as e:
        raise ClientValidationError(f"Failed to process registration data: {str(e)}")
    
    return registration_data

def validate_registration_key(registration_key: str) -> None:
    """Validate registration key against configured secret."""
    from backend.config import get_config
    
    config = get_config()
    expected_key = getattr(config, 'REGISTRATION_SECRET', None)
    
    if not expected_key:
        # No registration key required
        return
    
    if not registration_key:
        raise ClientValidationError("Registration key is required")
    
    if registration_key != expected_key:
        raise ClientValidationError("Invalid registration key")

def validate_client_registration_business_rules(raw_data: Dict[str, Any]) -> None:
    """Validate business rules for client registration."""
    
    # Validate client_id format
    client_id = raw_data.get('client_id')
    if client_id:
        validate_client_id_format(client_id)
    
    # Validate hostname
    hostname = raw_data.get('hostname', '')
    if hostname and not validate_hostname_format(hostname):
        raise ClientValidationError("Invalid hostname format")
    
    # Validate version format
    version = raw_data.get('version', '')
    if version and not validate_version_format(version):
        raise ClientValidationError("Invalid version format")
    
    # Validate platform
    platform = raw_data.get('platform', '')
    if platform and not validate_platform_format(platform):
        raise ClientValidationError("Invalid platform format")

def validate_client_id_format(client_id: str) -> bool:
    """Validate client ID format (UUID or similar)."""
    if not client_id or not isinstance(client_id, str):
        raise ClientValidationError("Client ID must be a non-empty string")
    
    # Allow UUID format or alphanumeric with hyphens/underscores
    if not re.match(r'^[a-zA-Z0-9\-_]{8,64}$', client_id):
        raise ClientValidationError("Client ID must be 8-64 characters, alphanumeric with hyphens/underscores only")
    
    return True

def validate_hostname_format(hostname: str) -> bool:
    """Validate hostname format."""
    if not hostname or len(hostname) > 255:
        return False
    
    # Basic hostname validation - alphanumeric, hyphens, dots
    return re.match(r'^[a-zA-Z0-9\-\.]+$', hostname) is not None

def validate_version_format(version: str) -> bool:
    """Validate version format (semantic versioning)."""
    if not version:
        return False
    
    # Allow semantic versioning: 1.0.0, 1.0.0-beta, etc.
    return re.match(r'^\d+\.\d+\.\d+(-[\w\.]+)?$', version) is not None

def validate_platform_format(platform: str) -> bool:
    """Validate platform format."""
    if not platform:
        return False
    
    valid_platforms = {'windows', 'darwin', 'linux', 'macos', 'win32', 'unix', 'unknown'}
    return platform.lower() in valid_platforms

# ============================================================================
# API Key Validation
# ============================================================================

def validate_api_key_format(api_key: str) -> None:
    """Validate API key format."""
    if not api_key or not isinstance(api_key, str):
        raise ApiKeyError("API key must be a non-empty string")
    
    # API keys should be hex strings of reasonable length
    if not re.match(r'^[a-fA-F0-9]{32,128}$', api_key):
        raise ApiKeyError("API key must be a hex string between 32-128 characters")

def validate_api_key_expiration(expires_at: str) -> None:
    """Validate API key expiration date."""
    if not expires_at:
        return  # No expiration is valid
    
    try:
        from datetime import datetime
        expires_dt = datetime.fromisoformat(expires_at)
        
        # Check if expiration is reasonable (not too far in future)
        max_years = 5
        max_expiry = datetime.now().replace(year=datetime.now().year + max_years)
        
        if expires_dt > max_expiry:
            raise ApiKeyError(f"API key expiration cannot be more than {max_years} years in the future")
            
    except ValueError:
        raise ApiKeyError("Invalid expiration date format")

# ============================================================================
# Client Update Validation
# ============================================================================

def validate_client_update_data(client_id: str, update_data: Dict[str, Any]) -> None:
    """Validate client update data."""
    if not client_id:
        raise ClientValidationError("Client ID is required for updates")
    
    validate_client_id_format(client_id)
    
    if not update_data or not isinstance(update_data, dict):
        raise ClientValidationError("Update data must be a non-empty dictionary")
    
    # Validate specific update fields if present
    if 'hostname' in update_data:
        hostname = update_data['hostname']
        if hostname and not validate_hostname_format(hostname):
            raise ClientValidationError("Invalid hostname format in update")
    
    if 'version' in update_data:
        version = update_data['version']
        if version and not validate_version_format(version):
            raise ClientValidationError("Invalid version format in update")
    
    if 'platform' in update_data:
        platform = update_data['platform']
        if platform and not validate_platform_format(platform):
            raise ClientValidationError("Invalid platform format in update")

# ============================================================================
# Security Validation
# ============================================================================

def validate_client_security_constraints(registration_data: ClientRegistrationData) -> None:
    """Validate security constraints for client registration."""
    
    # Rate limiting would be handled at the route level
    # This is for business-level security rules
    
    # Example: Prevent obviously fake hostnames
    hostname = registration_data.hostname.lower()
    suspicious_hostnames = ['test', 'fake', 'spam', 'bot', 'malicious']
    
    if any(suspicious in hostname for suspicious in suspicious_hostnames):
        logger.warning(f"Suspicious hostname in registration: {hostname}")
        # Don't reject, just log for monitoring
    
    # Example: Validate version is reasonable
    version = registration_data.version
    if version and version.startswith('0.'):
        logger.info(f"Development version registered: {version}")

def validate_client_permissions(client_id: str, requested_action: str) -> None:
    """Validate client permissions for specific actions."""
    # Placeholder for future permission system
    # For now, all registered clients have full upload permissions
    
    if not client_id:
        raise ClientValidationError("Client ID required for permission check")
    
    # Future: Check client status, subscription level, etc.
    # allowed_actions = get_client_permissions(client_id)
    # if requested_action not in allowed_actions:
    #     raise ClientValidationError(f"Client {client_id} not authorized for {requested_action}")
    
    pass