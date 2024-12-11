export { StatsEngine } from "back-end/src/models/ProjectModel";

import type { MetricStats } from "./metric";

export type PValueCorrection = null | "benjamini-hochberg" | "holm-bonferroni";

export type DifferenceType = "relative" | "absolute" | "scaled";

export type RiskType = "relative" | "absolute";

interface BaseVariationResponse {
  cr: number;
  value: number;
  users: number;
  denominator?: number;
  stats: MetricStats;
  expected?: number;
  uplift?: {
    dist: string;
    mean?: number;
    stddev?: number;
  };
  ci?: [number, number];
  errorMessage?: string;
}

interface BayesianVariationResponse extends BaseVariationResponse {
  chanceToWin?: number;
  risk?: [number, number];
  riskType?: RiskType;
}

interface FrequentistVariationResponse extends BaseVariationResponse {
  pValue?: number;
}

interface BaseDimensionResponse {
  dimension: string;
  srm: number;
}

interface BayesianDimensionResponse extends BaseDimensionResponse {
  variations: BayesianVariationResponse[];
}

interface FrequentistVariationResponse extends BaseDimensionResponse {
  variations: FrequentistVariationResponse[];
}

type StatsEngineDimensionResponse =
  | BayesianDimensionResponse
  | FrequentistVariationResponse;

// Keep below classes in sync with gbstats
export type ExperimentMetricAnalysis = {
  metric: string;
  analyses: {
    unknownVariations: string[];
    multipleExposures: number;
    // new output somewhere in here
    // not sure if here or inside DimensionResponse
    powerResult: {
      dailyTraffic: number;
      variationId: string;
      effectSize: number;
      power: string; // or number?
      // Do we want to have this in the response? or should we have a low/high power threshold in the FE/BE and use the power property?
      isLowPowered: boolean;
      // Should likely be in days to provide better flexibility
      timeRemainingDays: number;
    };
    dimensions: StatsEngineDimensionResponse[];
  }[];
}[];

export type SingleVariationResult = {
  users?: number;
  cr?: number;
  ci?: [number, number];
};

export type BanditResult = {
  singleVariationResults?: SingleVariationResult[];
  currentWeights: number[];
  updatedWeights: number[];
  srm: number;
  bestArmProbabilities?: number[];
  seed: number;
  updateMessage?: string;
  error?: string;
  reweight?: boolean;
};

export type MultipleExperimentMetricAnalysis = {
  id: string;
  results: ExperimentMetricAnalysis;
  banditResult?: BanditResult;
  error?: string;
  traceback?: string;
};
