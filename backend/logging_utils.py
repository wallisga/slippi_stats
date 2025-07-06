"""
Logging utilities and decorators for Slippi Server.

This module provides standardized logging decorators and utilities
for consistent structured logging across all backend functions.
"""

import functools
import logging
import time
import traceback
import inspect
from contextlib import contextmanager
from typing import Any, Dict, Optional, Callable
from backend.config import get_config

# Get configuration
config = get_config()


def get_structured_logger(module_name: str) -> logging.Logger:
    """
    Get a structured logger for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'web_service', 'database')
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'SlippiServer.{module_name}')


def log_function_execution(
    log_level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
    mask_sensitive: bool = True
):
    """
    Decorator to automatically log function execution with structured data.
    
    Args:
        log_level: Logging level for success cases
        include_args: Whether to log function arguments
        include_result: Whether to log return values
        mask_sensitive: Whether to mask sensitive data in logs
        
    Usage:
        @log_function_execution(log_level=logging.INFO, include_args=True)
        def my_function(param1, param2):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger for this module
            module_name = func.__module__.split('.')[-1] if '.' in func.__module__ else func.__module__
            logger = get_structured_logger(module_name)
            
            # Get correlation ID from kwargs or generate new one
            correlation_id = kwargs.get('correlation_id') or getattr(kwargs.get('request'), 'correlation_id', None)
            if not correlation_id and config.ENABLE_CORRELATION_ID:
                correlation_id = config.generate_correlation_id()
            
            start_time = time.time()
            
            # Prepare context data
            context = {
                "function_signature": str(inspect.signature(func))
            }
            
            if include_args:
                # Sanitize arguments for logging
                sanitized_args = _sanitize_args(args, kwargs) if mask_sensitive else {"args": args, "kwargs": kwargs}
                context["arguments"] = sanitized_args
            
            # Log function start
            logger.log(log_level, f"Function {func.__name__} started", extra={
                "source_function": func.__name__,
                "source_module": module_name,
                "correlation_id": correlation_id,
                "context": context
            })
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Prepare success context
                success_context = {"execution_time_ms": execution_time}
                if include_result and result is not None:
                    success_context["result_type"] = type(result).__name__
                    if isinstance(result, (dict, list)) and len(str(result)) < 1000:
                        success_context["result"] = result
                
                # Log successful completion
                logger.log(log_level, f"Function {func.__name__} completed successfully", extra={
                    "source_function": func.__name__,
                    "source_module": module_name,
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "context": success_context
                })
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                # Log error
                logger.error(f"Function {func.__name__} failed", extra={
                    "source_function": func.__name__,
                    "source_module": module_name,
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "error_code": type(e).__name__,
                    "context": {
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                })
                raise
                
        return wrapper
    return decorator


def log_database_operation(operation_type: str = "query"):
    """
    Decorator specifically for database operations.
    
    Args:
        operation_type: Type of database operation (query, insert, update, delete)
        
    Usage:
        @log_database_operation("insert")
        def create_game_record(game_data):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_structured_logger('database')
            
            correlation_id = kwargs.get('correlation_id')
            start_time = time.time()
            
            # Log operation start
            logger.debug(f"Database operation {func.__name__} started", extra={
                "source_function": func.__name__,
                "source_module": "database",
                "correlation_id": correlation_id,
                "context": {
                    "operation_type": operation_type,
                    "param_count": len(args) + len(kwargs)
                }
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Determine result info
                result_info = {}
                if isinstance(result, list):
                    result_info["row_count"] = len(result)
                elif isinstance(result, dict):
                    result_info["result_type"] = "single_row"
                elif result is not None:
                    result_info["result_type"] = type(result).__name__
                else:
                    result_info["result_type"] = "none"
                
                logger.debug(f"Database operation {func.__name__} completed", extra={
                    "source_function": func.__name__,
                    "source_module": "database",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "context": {
                        "operation_type": operation_type,
                        **result_info
                    }
                })
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(f"Database operation {func.__name__} failed", extra={
                    "source_function": func.__name__,
                    "source_module": "database",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "error_code": "DB_OPERATION_FAILED",
                    "context": {
                        "operation_type": operation_type,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e)
                    }
                })
                raise
                
        return wrapper
    return decorator


def log_api_endpoint(endpoint_name: str = None):
    """
    Decorator for API endpoint functions.
    
    Args:
        endpoint_name: Name of the API endpoint
        
    Usage:
        @log_api_endpoint("upload_games")
        def handle_upload_games():
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_structured_logger('api_service')
            
            name = endpoint_name or func.__name__
            correlation_id = kwargs.get('correlation_id')
            start_time = time.time()
            
            # Extract request info if available
            request_info = {}
            if hasattr(kwargs.get('request'), 'method'):
                request = kwargs['request']
                request_info = {
                    "method": request.method,
                    "path": request.path,
                    "user_agent": request.headers.get('User-Agent'),
                    "content_length": request.content_length,
                    "remote_addr": request.remote_addr
                }
            
            logger.info(f"API endpoint {name} called", extra={
                "source_function": func.__name__,
                "source_module": "api_service",
                "correlation_id": correlation_id,
                "context": {
                    "endpoint": name,
                    **request_info
                }
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Extract response info
                response_info = {}
                if hasattr(result, 'status_code'):
                    response_info["status_code"] = result.status_code
                if hasattr(result, 'content_length'):
                    response_info["content_length"] = result.content_length
                
                logger.info(f"API endpoint {name} completed", extra={
                    "function": func.__name__,
                    "module": "api_service",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "context": {
                        "endpoint": name,
                        **response_info
                    }
                })
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(f"API endpoint {name} failed", extra={
                    "source_function": func.__name__,
                    "source_module": "api_service",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "error_code": "API_ENDPOINT_FAILED",
                    "context": {
                        "endpoint": name,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        **request_info
                    }
                })
                raise
                
        return wrapper
    return decorator


def log_file_operation(operation_type: str):
    """
    Decorator for file operations (upload, download, delete).
    
    Args:
        operation_type: Type of file operation
        
    Usage:
        @log_file_operation("upload")
        def process_file_upload(file_data, metadata):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_structured_logger('api_service')
            
            correlation_id = kwargs.get('correlation_id')
            start_time = time.time()
            
            # Extract file info from arguments if available
            file_info = {}
            if args:
                # Try to extract file size and type from common argument patterns
                for arg in args:
                    if hasattr(arg, '__len__') and not isinstance(arg, str):
                        file_info["file_size_bytes"] = len(arg)
                        break
            
            if 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
                metadata = kwargs['metadata']
                file_info.update({
                    "filename": metadata.get('filename'),
                    "content_type": metadata.get('content_type')
                })
            
            logger.info(f"File operation {operation_type} started", extra={
                "source_function": func.__name__,
                "source_module": "api_service",
                "correlation_id": correlation_id,
                "context": {
                    "operation_type": operation_type,
                    **file_info
                }
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Extract result info
                result_info = {}
                if isinstance(result, dict):
                    if 'file_path' in result:
                        result_info["file_saved"] = True
                        result_info["file_path"] = result['file_path']
                    if 'file_hash' in result:
                        result_info["file_hash"] = result['file_hash']
                    if 'duplicate' in result:
                        result_info["duplicate_detected"] = result['duplicate']
                
                logger.info(f"File operation {operation_type} completed", extra={
                    "source_function": func.__name__,
                    "source_module": "api_service",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "context": {
                        "operation_type": operation_type,
                        **file_info,
                        **result_info
                    }
                })
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(f"File operation {operation_type} failed", extra={
                    "source_function": func.__name__,
                    "source_module": "api_service",
                    "correlation_id": correlation_id,
                    "execution_time_ms": execution_time,
                    "error_code": "FILE_OPERATION_FAILED",
                    "context": {
                        "operation_type": operation_type,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        **file_info
                    }
                })
                raise
                
        return wrapper
    return decorator


@contextmanager
def log_context(logger_name: str, operation: str, **context_data):
    """
    Context manager for logging operation start/end with timing.
    
    Args:
        logger_name: Name of the logger to use
        operation: Description of the operation
        **context_data: Additional context data to include
        
    Usage:
        with log_context('database', 'batch_insert', table='games', count=100):
            # perform operation
            pass
    """
    logger = get_structured_logger(logger_name)
    start_time = time.time()
    
    logger.debug(f"Operation {operation} started", extra={
        "source_function": operation,
        "source_module": logger_name,
        "context": context_data
    })
    
    try:
        yield
        execution_time = (time.time() - start_time) * 1000
        
        logger.debug(f"Operation {operation} completed", extra={
            "source_function": operation,
            "source_module": logger_name,
            "execution_time_ms": execution_time,
            "context": context_data
        })
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        
        logger.error(f"Operation {operation} failed", extra={
            "source_function": operation,
            "source_module": logger_name,
            "execution_time_ms": execution_time,
            "error_code": type(e).__name__,
            "context": {
                **context_data,
                "exception_type": type(e).__name__,
                "exception_message": str(e)
            }
        })
        raise


def log_business_event(event_name: str, **event_data):
    """
    Log important business events for analytics and monitoring.
    
    Args:
        event_name: Name of the business event
        **event_data: Event-specific data
        
    Usage:
        log_business_event('player_searched', player_code='PLAYER#123', games_found=25)
        log_business_event('file_uploaded', client_id='client_123', file_size=1024000)
    """
    logger = get_structured_logger('business_events')
    
    logger.info(f"Business event: {event_name}", extra={
        "source_function": "business_event",
        "source_module": "business_events",
        "context": {
            "event_name": event_name,
            "event_timestamp": time.time(),
            **event_data
        }
    })


def _sanitize_args(args: tuple, kwargs: dict) -> dict:
    """
    Sanitize function arguments for logging by masking sensitive data.
    
    Args:
        args: Function positional arguments
        kwargs: Function keyword arguments
        
    Returns:
        Sanitized arguments dictionary
    """
    sensitive_keys = {
        'password', 'token', 'secret', 'key', 'auth', 'credential',
        'api_key', 'session', 'csrf', 'registration_secret'
    }
    
    def sanitize_value(key: str, value: Any) -> Any:
        """Sanitize individual values based on key name."""
        if isinstance(key, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
            return "***MASKED***"
        
        if isinstance(value, dict):
            return {k: sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(f"item_{i}", item) for i, item in enumerate(value)]
        elif isinstance(value, str) and len(value) > 1000:
            return f"{value[:100]}... [truncated {len(value)} chars]"
        else:
            return value
    
    sanitized = {
        "args": [sanitize_value(f"arg_{i}", arg) for i, arg in enumerate(args)],
        "kwargs": {k: sanitize_value(k, v) for k, v in kwargs.items()}
    }
    
    return sanitized


def log_performance_metric(metric_name: str, value: float, unit: str = "ms", **tags):
    """
    Log performance metrics for monitoring and alerting.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **tags: Additional tags for the metric
        
    Usage:
        log_performance_metric('database_query_time', 250.5, 'ms', query_type='select')
        log_performance_metric('file_upload_size', 1024000, 'bytes', client_id='client_123')
    """
    logger = get_structured_logger('metrics')
    
    logger.info(f"Performance metric: {metric_name}", extra={
        "source_function": "performance_metric",
        "source_module": "metrics",
        "context": {
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "metric_timestamp": time.time(),
            **tags
        }
    })


def log_security_event(event_type: str, severity: str = "medium", **event_data):
    """
    Log security-related events for monitoring and alerting.
    
    Args:
        event_type: Type of security event
        severity: Severity level (low, medium, high, critical)
        **event_data: Event-specific data
        
    Usage:
        log_security_event('invalid_api_key', 'high', client_ip='192.168.1.1')
        log_security_event('rate_limit_exceeded', 'medium', endpoint='/api/upload')
    """
    logger = get_structured_logger('security')
    
    # Map severity to log level
    severity_map = {
        'low': logging.INFO,
        'medium': logging.WARNING,
        'high': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    log_level = severity_map.get(severity.lower(), logging.WARNING)
    
    logger.log(log_level, f"Security event: {event_type}", extra={
        "source_function": "security_event",
        "source_module": "security",
        "error_code": "SECURITY_EVENT",
        "context": {
            "event_type": event_type,
            "severity": severity,
            "event_timestamp": time.time(),
            **event_data
        }
    })


# Convenience functions for common logging patterns
def log_user_action(action: str, user_id: str = None, **action_data):
    """Log user actions for audit trails."""
    log_business_event('user_action', action=action, user_id=user_id, **action_data)


def log_api_request(endpoint: str, method: str, **request_data):
    """Log API requests for monitoring."""
    log_business_event('api_request', endpoint=endpoint, method=method, **request_data)


def log_error_recovery(error_type: str, recovery_action: str, **recovery_data):
    """Log error recovery actions."""
    logger = get_structured_logger('error_recovery')
    logger.warning(f"Error recovery: {recovery_action}", extra={
        "source_function": "error_recovery",
        "source_module": "error_recovery",
        "error_code": "ERROR_RECOVERY",
        "context": {
            "error_type": error_type,
            "recovery_action": recovery_action,
            **recovery_data
        }
    })


# Example usage patterns for documentation
if __name__ == "__main__":
    # These examples show how to use the logging utilities
    
    # Example 1: Function decorator
    @log_function_execution(log_level=logging.INFO, include_args=True)
    def example_service_function(player_code, limit=10):
        # Function implementation
        return {"games": [], "total": 0}
    
    # Example 2: Database operation
    @log_database_operation("select")
    def example_database_function(player_id):
        # Database query implementation
        return []
    
    # Example 3: API endpoint
    @log_api_endpoint("player_profile")
    def example_api_function(request):
        # API endpoint implementation
        return {"status": "success"}
    
    # Example 4: Context manager
    def example_context_usage():
        with log_context('data_processing', 'calculate_player_stats', player_count=100):
            # Perform calculations
            pass
    
    # Example 5: Business events
    def example_business_events():
        log_business_event('player_profile_viewed', player_code='PLAYER#123')
        log_performance_metric('response_time', 245.7, 'ms', endpoint='player_profile')
        log_security_event('invalid_api_key', 'high', client_ip='192.168.1.1')