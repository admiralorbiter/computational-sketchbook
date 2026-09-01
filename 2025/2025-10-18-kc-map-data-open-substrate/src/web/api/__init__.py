# API Blueprint Registration

from .base import BaseAPI
from .crime import CrimeAPI
from .service_requests import ServiceRequestsAPI
from .osm import OSMAPI
from .combined import CombinedAPI
from .settings import SettingsAPI

__all__ = ['BaseAPI', 'CrimeAPI', 'ServiceRequestsAPI', 'OSMAPI', 'CombinedAPI', 'SettingsAPI']
