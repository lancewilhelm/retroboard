<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";

// State
const availableApps = ref([]);
const currentApp = ref(null);
const selectedApp = ref(null);
const isConnected = ref(false);
const error = ref(null);
const isDarkTheme = ref(true); // Default to dark theme
const lastKnownApp = ref(null);

// App Configurations
const clockConfig = ref({
    font: "tom-thumb",
    color: [0, 255, 255],
});

const scrollConfig = ref({
    text: "Hello, World!",
    font: "tom-thumb",
    color: [255, 255, 255],
    speed: 1,
    fps: 30,
});

const starsConfig = ref({
    spawn_rate: 1,
    lifetime: 40,
    fps: 60,
});

// Polling interval reference
let pollInterval = null;

// API Base URL
const API_BASE = "/api";

// Utility Functions
function rgbToHex(rgb) {
    const [r, g, b] = rgb;
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

function formatAppName(name) {
    return name
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}

function getAppIcon(app) {
    const icons = {
        clock: "🕐",
        scroll_text: "📜",
        stars: "✨",
    };
    return icons[app] || "📱";
}

function getAppConfig(app) {
    const configs = {
        clock: clockConfig.value,
        scroll_text: scrollConfig.value,
        stars: starsConfig.value,
    };
    return configs[app] || {};
}

function toggleTheme() {
    isDarkTheme.value = !isDarkTheme.value;
    localStorage.setItem(
        "retroboard-theme",
        isDarkTheme.value ? "dark" : "light",
    );
}

// API Functions
async function fetchApps() {
    try {
        const response = await fetch(`${API_BASE}/apps`);
        const data = await response.json();
        availableApps.value = data.apps;
        currentApp.value = data.current;
        isConnected.value = true;
        error.value = null;
    } catch (err) {
        error.value = "Failed to connect to RetroBoard server";
        isConnected.value = false;
        console.error("Error fetching apps:", err);
    }
}

async function fetchCurrentAppOnly() {
    try {
        const response = await fetch(`${API_BASE}/current`);
        const data = await response.json();

        // Only update the current app name, not the config
        // This prevents overwriting user edits
        currentApp.value = data.app;
        isConnected.value = true;

        // If the app changed (e.g., switched via API), update config
        if (data.app !== lastKnownApp.value) {
            lastKnownApp.value = data.app;
            updateConfigFromServer(data.app, data.config);
        }
    } catch (err) {
        isConnected.value = false;
        console.error("Error fetching current app:", err);
    }
}

async function refreshConfig() {
    try {
        const response = await fetch(`${API_BASE}/current`);
        const data = await response.json();

        if (data.app && data.config) {
            updateConfigFromServer(data.app, data.config);
            error.value = null;
        }
    } catch (err) {
        error.value = "Failed to refresh configuration";
        console.error("Error refreshing config:", err);
    }
}

function updateConfigFromServer(app, config) {
    if (!config) return;

    if (app === "clock" && config.color) {
        clockConfig.value = { ...clockConfig.value, ...config };
    } else if (app === "scroll_text") {
        scrollConfig.value = { ...scrollConfig.value, ...config };
    } else if (app === "stars") {
        starsConfig.value = { ...starsConfig.value, ...config };
    }
}

async function switchApp() {
    if (!selectedApp.value) return;

    const config = getAppConfig(selectedApp.value);
    const isUpdatingCurrentApp = selectedApp.value === currentApp.value;

    try {
        let response;

        if (isUpdatingCurrentApp) {
            // Update config of running app without restarting
            response = await fetch(`${API_BASE}/config`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(config),
            });
        } else {
            // Switch to a different app
            response = await fetch(`${API_BASE}/switch`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    app: selectedApp.value,
                    config: config,
                }),
            });
        }

        if (response.ok) {
            if (!isUpdatingCurrentApp) {
                currentApp.value = selectedApp.value;
                lastKnownApp.value = selectedApp.value;
            }
            error.value = null;
        } else {
            const data = await response.json();
            error.value =
                data.error ||
                (isUpdatingCurrentApp
                    ? "Failed to update config"
                    : "Failed to switch app");
        }
    } catch (err) {
        error.value = "Failed to communicate with server";
        console.error("Error switching app:", err);
    }
}

async function stopApp() {
    try {
        const response = await fetch(`${API_BASE}/stop`, {
            method: "POST",
        });

        if (response.ok) {
            currentApp.value = null;
            lastKnownApp.value = null;
            selectedApp.value = null;
            error.value = null;
        } else {
            error.value = "Failed to stop app";
        }
    } catch (err) {
        error.value = "Failed to communicate with server";
        console.error("Error stopping app:", err);
    }
}

function selectApp(app) {
    selectedApp.value = app;
}

// Lifecycle
onMounted(async () => {
    // Load theme preference
    const savedTheme = localStorage.getItem("retroboard-theme");
    if (savedTheme) {
        isDarkTheme.value = savedTheme === "dark";
    }

    // Initial fetch
    await fetchApps();

    // Fetch current app and config on first load
    try {
        const response = await fetch(`${API_BASE}/current`);
        const data = await response.json();
        currentApp.value = data.app;
        lastKnownApp.value = data.app;

        if (data.app && data.config) {
            updateConfigFromServer(data.app, data.config);
        }
    } catch (err) {
        console.error("Error fetching initial config:", err);
    }

    // Poll only for app name changes, not config
    // This prevents overwriting user edits
    pollInterval = setInterval(async () => {
        await fetchCurrentAppOnly();
    }, 2000);
});

onUnmounted(() => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});
</script>

<template>
    <div class="app" :class="{ 'dark-theme': isDarkTheme }">
        <header class="header">
            <h1>🎮 RetroBoard Controller</h1>
            <div class="header-actions">
                <button
                    @click="toggleTheme"
                    class="btn-icon"
                    :title="isDarkTheme ? 'Light Mode' : 'Dark Mode'"
                >
                    {{ isDarkTheme ? "☀️" : "🌙" }}
                </button>
                <div class="status" :class="{ connected: isConnected }">
                    <span class="status-dot"></span>
                    {{ isConnected ? "Connected" : "Disconnected" }}
                </div>
            </div>
        </header>

        <main class="main">
            <!-- Current App Display -->
            <section class="current-app">
                <h2>Current App</h2>
                <div class="app-display">
                    <div class="app-name">{{ currentApp || "None" }}</div>
                    <div class="app-actions">
                        <button
                            @click="refreshConfig"
                            class="btn btn-secondary"
                            :disabled="!currentApp"
                            title="Refresh config from server"
                        >
                            🔄 Refresh
                        </button>
                        <button
                            @click="stopApp"
                            class="btn btn-danger"
                            :disabled="!currentApp"
                        >
                            Stop App
                        </button>
                    </div>
                </div>
            </section>

            <!-- App Switcher -->
            <section class="app-switcher">
                <h2>Available Apps</h2>
                <div class="app-grid">
                    <div
                        v-for="app in availableApps"
                        :key="app"
                        class="app-card"
                        :class="{ active: app === currentApp }"
                        @click="selectApp(app)"
                    >
                        <div class="app-icon">{{ getAppIcon(app) }}</div>
                        <div class="app-label">{{ formatAppName(app) }}</div>
                    </div>
                </div>
            </section>

            <!-- App Configuration -->
            <section v-if="selectedApp" class="app-config">
                <h2>{{ formatAppName(selectedApp) }} Configuration</h2>

                <!-- Clock App Config -->
                <div v-if="selectedApp === 'clock'" class="config-form">
                    <div class="form-group">
                        <label>Font:</label>
                        <select v-model="clockConfig.font" class="input">
                            <option value="tom-thumb">Tom Thumb</option>
                            <option value="6x10">6x10</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Color:</label>
                        <div class="color-inputs">
                            <input
                                type="number"
                                v-model.number="clockConfig.color[0]"
                                min="0"
                                max="255"
                                placeholder="R"
                                class="input input-sm"
                            />
                            <input
                                type="number"
                                v-model.number="clockConfig.color[1]"
                                min="0"
                                max="255"
                                placeholder="G"
                                class="input input-sm"
                            />
                            <input
                                type="number"
                                v-model.number="clockConfig.color[2]"
                                min="0"
                                max="255"
                                placeholder="B"
                                class="input input-sm"
                            />
                        </div>
                        <div
                            class="color-preview"
                            :style="{
                                backgroundColor: rgbToHex(clockConfig.color),
                            }"
                        ></div>
                    </div>
                </div>

                <!-- Scroll Text App Config -->
                <div
                    v-else-if="selectedApp === 'scroll_text'"
                    class="config-form"
                >
                    <div class="form-group">
                        <label>Text:</label>
                        <input
                            type="text"
                            v-model="scrollConfig.text"
                            class="input"
                            placeholder="Enter text to display"
                        />
                    </div>
                    <div class="form-group">
                        <label>Font:</label>
                        <select v-model="scrollConfig.font" class="input">
                            <option value="tom-thumb">Tom Thumb</option>
                            <option value="6x10">6x10</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Speed:</label>
                        <input
                            type="number"
                            v-model.number="scrollConfig.speed"
                            min="1"
                            max="10"
                            class="input"
                        />
                    </div>
                    <div class="form-group">
                        <label>FPS:</label>
                        <input
                            type="number"
                            v-model.number="scrollConfig.fps"
                            min="10"
                            max="60"
                            class="input"
                        />
                    </div>
                    <div class="form-group">
                        <label>Color:</label>
                        <div class="color-inputs">
                            <input
                                type="number"
                                v-model.number="scrollConfig.color[0]"
                                min="0"
                                max="255"
                                placeholder="R"
                                class="input input-sm"
                            />
                            <input
                                type="number"
                                v-model.number="scrollConfig.color[1]"
                                min="0"
                                max="255"
                                placeholder="G"
                                class="input input-sm"
                            />
                            <input
                                type="number"
                                v-model.number="scrollConfig.color[2]"
                                min="0"
                                max="255"
                                placeholder="B"
                                class="input input-sm"
                            />
                        </div>
                        <div
                            class="color-preview"
                            :style="{
                                backgroundColor: rgbToHex(scrollConfig.color),
                            }"
                        ></div>
                    </div>
                </div>

                <!-- Stars App Config -->
                <div v-else-if="selectedApp === 'stars'" class="config-form">
                    <div class="form-group">
                        <label>Spawn Rate:</label>
                        <input
                            type="number"
                            v-model.number="starsConfig.spawn_rate"
                            min="1"
                            max="10"
                            class="input"
                        />
                    </div>
                    <div class="form-group">
                        <label>Lifetime:</label>
                        <input
                            type="number"
                            v-model.number="starsConfig.lifetime"
                            min="10"
                            max="100"
                            class="input"
                        />
                    </div>
                    <div class="form-group">
                        <label>FPS:</label>
                        <input
                            type="number"
                            v-model.number="starsConfig.fps"
                            min="10"
                            max="120"
                            class="input"
                        />
                    </div>
                </div>

                <div class="form-actions">
                    <button @click="switchApp" class="btn btn-primary">
                        {{
                            selectedApp === currentApp
                                ? "Update Config"
                                : "Switch to App"
                        }}
                    </button>
                </div>
            </section>

            <!-- Error Display -->
            <div v-if="error" class="error-banner">
                {{ error }}
            </div>
        </main>
    </div>
</template>

<style scoped>
.app {
    min-height: 100vh;
    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
    padding: 2rem;
    transition: background 0.3s ease;
}

.app.dark-theme {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    color: white;
}

.header h1 {
    margin: 0;
    font-size: 2rem;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.btn-icon {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 0.5rem;
    padding: 0.5rem 0.75rem;
    font-size: 1.25rem;
    cursor: pointer;
    transition: all 0.2s;
    color: white;
}

.btn-icon:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
}

.status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2rem;
    font-size: 0.9rem;
}

.status-dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    background: #ef4444;
    animation: pulse-red 2s infinite;
}

.status.connected .status-dot {
    background: #10b981;
    animation: pulse-green 2s infinite;
}

@keyframes pulse-red {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

@keyframes pulse-green {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.main {
    max-width: 1200px;
    margin: 0 auto;
}

section {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition:
        background 0.3s ease,
        color 0.3s ease;
}

.dark-theme section {
    background: #1f2937;
    color: #e5e7eb;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
}

section h2 {
    margin-top: 0;
    color: #1f2937;
    font-size: 1.25rem;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.dark-theme section h2 {
    color: #f9fafb;
    border-bottom-color: #374151;
}

.app-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.app-name {
    font-size: 1.5rem;
    font-weight: bold;
    color: #667eea;
    text-transform: capitalize;
    flex: 1;
}

.dark-theme .app-name {
    color: #818cf8;
}

.app-actions {
    display: flex;
    gap: 0.5rem;
}

.app-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1rem;
}

.app-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
}

.dark-theme .app-card {
    background: #111827;
    border-color: #374151;
}

.app-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
}

.dark-theme .app-card:hover {
    border-color: #818cf8;
    box-shadow: 0 4px 6px rgba(129, 140, 248, 0.3);
}

.app-card.active {
    border-color: #667eea;
    background: #f3f4f6;
}

.dark-theme .app-card.active {
    border-color: #9ca3af;
    background: #374151;
}

.app-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.app-label {
    font-weight: 600;
    color: #374151;
    text-align: center;
}

.dark-theme .app-label {
    color: #d1d5db;
}

.config-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-weight: 600;
    color: #374151;
}

.dark-theme .form-group label {
    color: #d1d5db;
}

.input {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    background: white;
    color: #1f2937;
}

.dark-theme .input {
    background: #111827;
    border-color: #4b5563;
    color: #e5e7eb;
}

.input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.dark-theme .input:focus {
    border-color: #9ca3af;
    box-shadow: 0 0 0 3px rgba(156, 163, 175, 0.2);
}

.input-sm {
    width: 4rem;
}

.color-inputs {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.color-preview {
    width: 3rem;
    height: 3rem;
    border-radius: 0.375rem;
    border: 2px solid #d1d5db;
}

.dark-theme .color-preview {
    border-color: #4b5563;
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background: #667eea;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #5568d3;
}

.dark-theme .btn-primary {
    background: #4b5563;
}

.dark-theme .btn-primary:hover:not(:disabled) {
    background: #374151;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background: #4b5563;
}

.btn-danger {
    background: #ef4444;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background: #dc2626;
}

.error-banner {
    background: #fee2e2;
    border: 1px solid #fecaca;
    color: #991b1b;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-top: 1rem;
}

.dark-theme .error-banner {
    background: #991b1b;
    border-color: #b91c1c;
    color: #fecaca;
}
</style>
