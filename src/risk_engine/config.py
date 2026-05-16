"""
Configuration module for Identity Risk Scoring Engine.

Demonstrates centralized, environment-aware configuration management.
Follows the 12-factor app methodology for configuration.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from pathlib import Path
import json
import os


class Environment(Enum):
    """Deployment environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: int = 20
    max_overflow: int = 40
    echo: bool = False
    
    @property
    def connection_string(self) -> str:
        """Build database connection string."""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    ttl_seconds: int = 3600
    max_entries: int = 10000
    # For Redis: "redis://localhost:6379/0"
    backend_url: str = "memory"


@dataclass
class RiskScoringConfig:
    """Risk scoring thresholds and weights."""
    # Risk score thresholds
    low_risk_threshold: float = 0.4
    medium_risk_threshold: float = 0.6
    high_risk_threshold: float = 0.8
    
    # Factor weights (must sum to 1.0)
    behavioral_weight: float = 0.40
    compliance_weight: float = 0.35
    anomaly_weight: float = 0.25
    
    # Behavioral risk parameters
    hours_of_operation_start: int = 8  # 8 AM
    hours_of_operation_end: int = 18   # 6 PM
    max_geographic_distance_km: float = 100
    max_login_velocity_km_per_hour: float = 900  # Realistic travel speed
    
    # Anomaly detection parameters
    statistical_outlier_threshold: float = 3.0  # Standard deviations
    concurrent_session_limit: int = 3
    failed_login_attempt_limit: int = 5
    failed_login_window_minutes: int = 15
    
    # Compliance parameters
    max_password_age_days: int = 90
    mfa_required_for_admins: bool = True
    require_https: bool = True


@dataclass
class AuditConfig:
    """Audit and compliance configuration."""
    enabled: bool = True
    immutable: bool = True
    log_all_access: bool = True
    retention_days: int = 2555  # 7 years
    archive_to_s3: bool = False
    s3_bucket: Optional[str] = None
    
    # Compliance standards
    soc2_mode: bool = True
    hipaa_mode: bool = False
    pci_dss_mode: bool = False


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    # Session configuration
    session_timeout_minutes: int = 30
    session_absolute_timeout_hours: int = 8
    
    # Token configuration
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Password policy
    min_password_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    
    # MFA configuration
    mfa_provider: str = "totp"  # totp, sms, push
    mfa_timeout_seconds: int = 300
    
    # CORS configuration
    allowed_origins: list = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:3000"]


@dataclass
class Config:
    """Main configuration container."""
    environment: Environment
    log_level: LogLevel
    database: DatabaseConfig
    cache: CacheConfig
    risk_scoring: RiskScoringConfig
    audit: AuditConfig
    security: SecurityConfig
    
    # Feature flags
    enable_policy_engine: bool = True
    enable_anomaly_detection: bool = True
    enable_audit_logging: bool = True
    
    # Performance tuning
    risk_calculation_timeout_ms: int = 100
    policy_evaluation_timeout_ms: int = 50
    
    @classmethod
    def from_environment(cls) -> "Config":
        """Load configuration from environment variables."""
        env = Environment(os.getenv("ENVIRONMENT", "development"))
        log_level = LogLevel(os.getenv("LOG_LEVEL", "INFO"))
        
        database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            username=os.getenv("DB_USER", "risk_engine"),
            password=os.getenv("DB_PASSWORD", "dev_password"),
            database=os.getenv("DB_NAME", "risk_engine"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
        )
        
        cache = CacheConfig(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl_seconds=int(os.getenv("CACHE_TTL", "3600")),
            backend_url=os.getenv("CACHE_URL", "memory"),
        )
        
        security = SecurityConfig(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-prod"),
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT", "30")),
        )
        
        audit = AuditConfig(
            enabled=os.getenv("AUDIT_ENABLED", "true").lower() == "true",
            immutable=os.getenv("AUDIT_IMMUTABLE", "true").lower() == "true",
            hipaa_mode=os.getenv("HIPAA_MODE", "false").lower() == "true",
            soc2_mode=os.getenv("SOC2_MODE", "true").lower() == "true",
        )
        
        return cls(
            environment=env,
            log_level=log_level,
            database=database,
            cache=cache,
            risk_scoring=RiskScoringConfig(),
            audit=audit,
            security=security,
        )
    
    @classmethod
    def from_file(cls, config_file: Path) -> "Config":
        """Load configuration from JSON file."""
        with open(config_file) as f:
            data = json.load(f)
        
        return cls(
            environment=Environment(data["environment"]),
            log_level=LogLevel(data["log_level"]),
            database=DatabaseConfig(**data["database"]),
            cache=CacheConfig(**data["cache"]),
            risk_scoring=RiskScoringConfig(**data.get("risk_scoring", {})),
            audit=AuditConfig(**data.get("audit", {})),
            security=SecurityConfig(**data.get("security", {})),
        )


# Global configuration instance (initialized at startup)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_environment()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance (typically for testing)."""
    global _config
    _config = config
