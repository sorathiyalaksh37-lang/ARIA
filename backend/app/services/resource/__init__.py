"""
Resource Service Package
Exposes ResourcePredictor, ResourceAllocator, and ResourceOptimizer singletons.
"""

from app.services.resource.predictor import resource_predictor, ResourcePredictor
from app.services.resource.allocator import resource_allocator, ResourceAllocator
from app.services.resource.optimizer import resource_optimizer, ResourceOptimizer

__all__ = [
    "resource_predictor",
    "ResourcePredictor",
    "resource_allocator",
    "ResourceAllocator",
    "resource_optimizer",
    "ResourceOptimizer",
]
