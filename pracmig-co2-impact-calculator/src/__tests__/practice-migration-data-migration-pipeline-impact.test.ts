import {
  AWS_CLOUD_CONSTANTS,
  AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH,
} from "@cloud-carbon-footprint/aws";
import {
  ComputeEstimator,
  COMPUTE_PROCESSOR_TYPES,
  NetworkingEstimator,
  StorageEstimator,
} from "@cloud-carbon-footprint/core";

describe("Impact calculator for a single migration", () => {
  it("calculates network usage impact", () => {
    // AWS_CLOUD_CONSTANTS.NETWORKING_COEFFICIENT is for internal AWS networking…
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
      powerUsageEffectiveness: AWS_CLOUD_CONSTANTS.getPUE(region),
    };

    const result = new NetworkingEstimator(networkingCoefficient).estimate(
      input,
      region,
      emissionsFactors,
      awsConstants
    );

    console.log("Network impact:");
    console.dir(result, { depth: 4, colors: true });
    expect(result).not.toBeNull();
  });

  it("calculates S3 storage usage impact", () => {
    const networkingCoefficient = AWS_CLOUD_CONSTANTS.NETWORKING_COEFFICIENT;
    const region = "eu-west-2";
    const emissionsFactors = AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH;
    const input = [
      {
        // 5 days
        terabyteHours: 5 * 24,
      },
    ];
    const awsConstants = {
      powerUsageEffectiveness: AWS_CLOUD_CONSTANTS.getPUE(region),
    };

    const result = new StorageEstimator(networkingCoefficient).estimate(
      input,
      region,
      emissionsFactors,
      awsConstants
    );

    console.log("Target supplier s3 bucket impact:");
    console.dir(result, { depth: 4, colors: true });
    expect(result).not.toBeNull();
  });

  it("calculates DataSync Agent usage impact", () => {
    const region = "eu-west-2";
    const emissionsFactors = AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH;
    const input = [
      {
        cpuUtilizationAverage: AWS_CLOUD_CONSTANTS.AVG_CPU_UTILIZATION_2020,
        // 8 vCPUs (for an m5.2xlarge) * 24 hours * 5 days
        numberOfvCpus: 8 * 24 * 5,
        usesAverageCPUConstant: true,
      },
    ];
    // COMPUTE_PROCESSOR_TYPES.SKYLAKE taken from INSTANCE_TYPE_COMPUTE_PROCESSOR_MAPPING['m5.2xlarge']
    const awsConstants = {
      minWatts: AWS_CLOUD_CONSTANTS.getMinWatts([
        COMPUTE_PROCESSOR_TYPES.SKYLAKE,
      ]),
      maxWatts: AWS_CLOUD_CONSTANTS.getMaxWatts([
        COMPUTE_PROCESSOR_TYPES.SKYLAKE,
      ]),
      powerUsageEffectiveness: AWS_CLOUD_CONSTANTS.getPUE(region),
      // The agent will be on-premise so will likely not have replication
      replicationFactor: 1,
    };

    const result = new ComputeEstimator().estimate(
      input,
      region,
      emissionsFactors,
      awsConstants
    );

    console.log("DataSync agent impact:");
    console.dir(result, { depth: 4, colors: true });
    expect(result).not.toBeNull();
  });

  it("calculates ACL updator lambda usage impact", () => {
    const region = "eu-west-2";
    const emissionsFactors = AWS_EMISSIONS_FACTORS_METRIC_TON_PER_KWH;
    // 1 vCPU (for lambdas using less than 1792MB of memory)
    const numberOfVCpus = 1;
    // 1 second lambda execution time in hours
    const lambdaExecutionDurationInHours = 1 / 3600;
    // number of files per patient * number of patients
    const numberOfFiles = 30 * 13000;
    const input = [
      {
        cpuUtilizationAverage: AWS_CLOUD_CONSTANTS.AVG_CPU_UTILIZATION_2020,
        numberOfvCpus:
          numberOfVCpus * lambdaExecutionDurationInHours * numberOfFiles,
        usesAverageCPUConstant: true,
      },
    ];
    // using the same value as for an m5.2xlarge, since I can't find anything better to use
    const awsConstants = {
      minWatts: AWS_CLOUD_CONSTANTS.getMinWatts([
        COMPUTE_PROCESSOR_TYPES.SKYLAKE,
      ]),
      maxWatts: AWS_CLOUD_CONSTANTS.getMaxWatts([
        COMPUTE_PROCESSOR_TYPES.SKYLAKE,
      ]),
      powerUsageEffectiveness: AWS_CLOUD_CONSTANTS.getPUE(region),
      replicationFactor: 1,
    };

    const result = new ComputeEstimator().estimate(
      input,
      region,
      emissionsFactors,
      awsConstants
    );

    console.log("ACL lambda usage:");
    console.dir(result, { depth: 4, colors: true });
    expect(result).not.toBeNull();
  });
});
