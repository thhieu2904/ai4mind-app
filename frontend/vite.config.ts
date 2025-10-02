import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
        "@/components": path.resolve(__dirname, "./src/components"),
        "@/pages": path.resolve(__dirname, "./src/pages"),
        "@/services": path.resolve(__dirname, "./src/services"),
        "@/types": path.resolve(__dirname, "./src/types"),
        "@/utils": path.resolve(__dirname, "./src/utils"),
        "@/hooks": path.resolve(__dirname, "./src/hooks"),
        "@/contexts": path.resolve(__dirname, "./src/contexts"),
      },
    },
    server: {
      port: 3000,
      proxy: {
        "/api": {
          target: env.VITE_API_URL || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
