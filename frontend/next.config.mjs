/** @type {import('next').NextConfig} */
const nextConfig = {
    httpAgentOptions: {
        keepAlive: false,
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:5000/api/:path*'
            }
        ]
    },
    experimental: {
        proxyTimeout: 10 * 60 * 1000
    }
};

export default nextConfig;
