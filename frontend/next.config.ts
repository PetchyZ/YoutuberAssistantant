import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use standalone output for Docker, default output for Netlify / Vercel
  ...(process.env.BUILD_STANDALONE === "true" ? { output: "standalone" } : {}),
};

export default nextConfig;
