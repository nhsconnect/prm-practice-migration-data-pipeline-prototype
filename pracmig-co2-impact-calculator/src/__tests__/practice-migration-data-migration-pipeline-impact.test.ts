import {
  AWS_CLOUD_CONSTANTS,
  AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
} from "@cloud-carbon-footprint/aws";
import { NetworkingEstimator } from "@cloud-carbon-footprint/core";

describe("Calculate impact", () => {
  it("should calculate network usage impact for a single migration", () => {
    const networkingCoefficient = AWS_CLOUD_CONSTANTS.NETWORKING_COEFFICIENT;
    const region = "eu-west-2";
    const emissionsFactors = AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH;
    const input = [
      {
        timestamp: new Date(),
        gigabytes: 1000,
      },
    ];
    const awsConstants = {
      powerUsageEffectiveness: 1.135,
    };
    const result = new NetworkingEstimator(networkingCoefficient).estimate(
      input,
      region,
      emissionsFactors,
      awsConstants
    );

    console.dir(result, { depth: 4, colors: true });
    expect(result).not.toBeNull();
  });
});
