import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // iTunes / Apple Music artwork CDN
    remotePatterns: [{ protocol: "https", hostname: "*.mzstatic.com" }],
  },
};

export default nextConfig;
