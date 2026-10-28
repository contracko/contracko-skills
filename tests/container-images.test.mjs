import { expect, test } from "bun:test";
import { scanImageSource } from "../scripts/check-container-images.mjs";

test("Docker actions accept a local Dockerfile", () => {
  const result = scanImageSource(
    ".github/actions/example/action.yml",
    "name: Example\nruns:\n  using: docker\n  image: Dockerfile\n",
  );

  expect(result).toEqual({ references: [], dynamic: [] });
});
