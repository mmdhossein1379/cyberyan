import type { NextConfig } from "next";
import { loadEnvFile } from "node:process";
import path from "node:path";

if (!process.env.BACKEND_URL) {
  try {
    loadEnvFile(
      path.resolve(process.cwd(), "../.env")
    );
  } catch {
    // Docker/build environment may provide variables directly.
  }
}

const backendUrl =
  process.env.BACKEND_URL ??
  (
    process.env.BACKEND_PORT
      ? `http://localhost:${process.env.BACKEND_PORT}`
      : undefined
  );

if (!backendUrl) {
  throw new Error(
    "BACKEND_URL or BACKEND_PORT is not defined"
  );
}

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
