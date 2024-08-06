import { MetricAnalysisPopulationType } from "@back-end/types/metric-analysis";
import React from "react";
import SelectField from "@/components/Forms/SelectField";
import { useDefinitions } from "@/services/DefinitionsContext";

export interface Props {
  value: string;
  setValue: (value: MetricAnalysisPopulationType) => void;
  setPopulationValue: (value: string | null) => void;

  userIdType: string;
  datasourceId: string;

  labelClassName?: string;
}

export default function PopulationChooser({
  value,
  setValue,
  setPopulationValue,
  userIdType,
  datasourceId,
  labelClassName,
}: Props) {
  const { getDatasourceById, segments } = useDefinitions();

  // get matching exposure queries
  const datasource = getDatasourceById(datasourceId);
  const availableExposureQueries = (
    datasource?.settings?.queries?.exposure || []
  )
    .filter((e) => e.userIdType === userIdType)
    .map((e) => ({
      label: `Experiment Exposed Units: ${e.name}`,
      value: `experiment_${e.id}`,
    }));

  // get matching segments
  const availableSegments = segments
    .filter((s) => s.datasource === datasourceId && s.userIdType === userIdType)
    .map((s) => {
      return {
        label: `Segment: ${s.name}`,
        value: `segment_${s.id}`,
      };
    });

  return (
    <div>
      <div className="uppercase-title text-muted">Population</div>
      <SelectField
        labelClassName={labelClassName}
        containerClassName={"select-dropdown-underline"}
        options={[
          {
            label: "Fact Table",
            options: [
              {
                label: `Fact Table (default)`,
                value: "factTable",
              },
            ],
          },
          ...(availableSegments.length > 0
            ? [
                {
                  label: `Joined Populations`,
                  options: [...availableSegments, ...availableExposureQueries],
                },
              ]
            : []),
        ]}
        sort={false}
        value={value}
        onChange={(v) => {
          if (v === value) return;
          if (v.startsWith("experiment")) {
            setValue("exposureQuery");
            const exposureQueryId = v.match(/experiment_(.*)/)?.[1];
            setPopulationValue(exposureQueryId ?? null);
          } else if (v.startsWith("segment")) {
            setValue("segment");
            const segmentId = v.match(/segment_(.*)/)?.[1];
            setPopulationValue(segmentId ?? null);
          } else {
            setValue(v as MetricAnalysisPopulationType);
            setPopulationValue(null);
          }
        }}
      />
    </div>
  );
}
