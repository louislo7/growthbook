from typing import List, Optional, Tuple, Union

from pydantic.dataclasses import dataclass

from gbstats.bayesian.tests import RiskType
from gbstats.models.tests import Uplift
from gbstats.models.settings import BanditWeightsByDate


# Data classes for return to the back end
@dataclass
class SingleVariationResult:
    users: Optional[float]
    cr: Optional[float]
    ci: Optional[List[float]]


@dataclass
class UserCountsByDate:
    date: str
    user_counts: List[float]


@dataclass
class UserPercentagesByDate:
    date: str
    user_counts: List[float]


@dataclass
class BanditSRMData:
    weights: List[BanditWeightsByDate]
    user_counts: Optional[List[UserCountsByDate]]
    user_percentages: Optional[List[UserPercentagesByDate]]


@dataclass
class BanditResult:
    singleVariationResults: Optional[List[SingleVariationResult]]
    banditSRMData: BanditSRMData
    weights: Optional[List[float]]
    bestArmProbabilities: Optional[List[float]]
    additionalReward: Optional[float]
    seed: int
    updateMessage: Optional[str]
    error: Optional[str]


@dataclass
class MetricStats:
    users: int
    count: int
    stddev: float
    mean: float


@dataclass
class BaselineResponse:
    cr: float
    value: float
    users: float
    denominator: Optional[float]
    stats: MetricStats


@dataclass
class BaseVariationResponse(BaselineResponse):
    expected: float
    uplift: Uplift
    ci: Tuple[float, float]
    errorMessage: Optional[str]


@dataclass
class BayesianVariationResponse(BaseVariationResponse):
    chanceToWin: float
    risk: Tuple[float, float]
    riskType: RiskType


@dataclass
class FrequentistVariationResponse(BaseVariationResponse):
    pValue: float


VariationResponse = Union[
    BayesianVariationResponse, FrequentistVariationResponse, BaselineResponse
]


@dataclass
class DimensionResponse:
    dimension: str
    srm: float
    variations: List[VariationResponse]


@dataclass
class ExperimentMetricAnalysisResult:
    unknownVariations: List[str]
    multipleExposures: float
    dimensions: List[DimensionResponse]


@dataclass
class ExperimentMetricAnalysis:
    metric: str
    analyses: List[ExperimentMetricAnalysisResult]


@dataclass
class MultipleExperimentMetricAnalysis:
    id: str
    results: List[ExperimentMetricAnalysis]
    banditResult: Optional[BanditResult]
    error: Optional[str]
