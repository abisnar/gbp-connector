"""OAuth authentication strategies."""

from gbp_connector.auth.base import AuthProvider
from gbp_connector.auth.oauth2 import OAuth2RefreshTokenProvider
from gbp_connector.auth.static import StaticTokenProvider

__all__ = ["AuthProvider", "OAuth2RefreshTokenProvider", "StaticTokenProvider"]
