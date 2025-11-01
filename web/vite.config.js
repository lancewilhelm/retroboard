import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server: {
        port: 3000,
        proxy: {
            // Proxy both HTTP API and WebSocket connections
            "/api": {
                target: "http://localhost:5000",
                changeOrigin: true,
            },
            "/socket.io": {
                target: "http://localhost:5000",
                changeOrigin: true,
                ws: true,
            },
        },
    },
});
