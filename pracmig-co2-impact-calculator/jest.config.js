/*
 * © 2021 Thoughtworks, Inc.
 */

// eslint-disable-next-line @typescript-eslint/no-var-requires
module.exports = {
  roots: ["<rootDir>/src"],
  transform: {
    "^.+\\.tsx?$": "ts-jest",
  },
  coverageReporters: ["json", "lcov", "text", "clover"],
  collectCoverageFrom: ["<rootDir>/src/**/*.ts"],
  coverageThreshold: {
    global: {
      statements: 99,
      branches: 88,
      functions: 100,
      lines: 99,
    },
  },
};
