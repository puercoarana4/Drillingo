/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow images from S3/Supabase Object Storage (Req 5.7)
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.amazonaws.com",
      },
      {
        protocol: "https",
        hostname: "**.supabase.co",
      },
    ],
  },
};

export default nextConfig;
