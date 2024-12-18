import { z } from "zod";
import {
  featurePrerequisite,
  savedGroupTargeting,
} from "back-end/src/validators/features";
import { statsEngines } from "back-end/src/util/constants";

export const experimentTemplateInterface = z
  .object({
    id: z.string(),
    organization: z.string(),
    projects: z.array(z.string()).default([]),
    owner: z.string(),
    dateCreated: z.date(),
    dateUpdated: z.date(),

    templateMetadata: z.object({
      name: z.string(),
      description: z.string().optional(),
      tags: z.array(z.string()).optional(),
    }),

    type: z.enum(["standard"]),
    hypothesis: z.string().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional(),

    datasource: z.string(),
    userIdType: z.enum(["anonymous", "user"]).optional(),
    exposureQueryId: z.string(),

    hashAttribute: z.string().optional(),
    fallbackAttribute: z.string().optional(),
    disableStickyBucketing: z.boolean().optional(),

    // Advanced
    // Add conversions windows

    goalMetrics: z.array(z.string()).optional(),
    secondaryMetrics: z.array(z.string()).optional(),
    guardrailMetrics: z.array(z.string()).optional(),
    activationMetric: z.string().optional().optional(),
    statsEngine: z.enum(statsEngines),

    // Located in phases array for ExperimentInterface
    targeting: z.object({
      coverage: z.number(),
      savedGroups: z.array(savedGroupTargeting).optional(),
      prerequisites: z.array(featurePrerequisite).optional(),
      condition: z.string().default("{}"),
    }),
  })
  .strict();
export type ExperimentTemplateInterface = z.infer<
  typeof experimentTemplateInterface
>;

export const createTemplateValidator = experimentTemplateInterface.omit({
  id: true,
  organization: true,
  owner: true,
  dateCreated: true,
  dateUpdated: true,
});
export type CreateTemplateProps = z.infer<typeof createTemplateValidator>;

export const updateTemplateValidator = experimentTemplateInterface.partial();

export type UpdateTemplateProps = z.infer<typeof updateTemplateValidator>;
