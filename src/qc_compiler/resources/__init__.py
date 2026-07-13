from qc_compiler.resources.depth import estimate_parallel_depth
from qc_compiler.resources.estimator import ResourceEstimate, ResourceEstimator
from qc_compiler.resources.expanded import (
    ExpandedResourceEstimate,
    estimate_toffoli_expanded_resources,
)

__all__ = [
    "ExpandedResourceEstimate",
    "ResourceEstimate",
    "ResourceEstimator",
    "estimate_parallel_depth",
    "estimate_toffoli_expanded_resources",
]
