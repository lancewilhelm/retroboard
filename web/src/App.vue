<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { io } from "socket.io-client";

// State
const availableApps = ref([]);
const currentApp = ref(null);
const selectedApp = ref(null);
const isConnected = ref(false);
const error = ref(null);
const isDarkTheme = ref(true); // Default to dark theme
const lastKnownApp = ref(null);
const brightness = ref(100); // 0-100

// Carousel/Rotation Mode
const carouselEnabled = ref(false);
const carouselApps = ref([]); // Array of {app: string, duration: number}
const editingCarousel = ref(false);

// App Configurations
const clockConfig = ref({
    font: "tom-thumb",
    color: [255, 255, 255],
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

// WebSocket connection
let socket = null;

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

// WebSocket Functions
function initializeWebSocket() {
    // Connect to WebSocket server through the proxy
    // Use polling as primary transport for reliability through Vite proxy
    socket = io({
        transports: ["polling", "websocket"],
        upgrade: true,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: Infinity,
        timeout: 20000,
        forceNew: false,
        multiplex: true,
    });

    socket.on("connect", () => {
        const transport = socket.io.engine.transport.name;
        console.log(`Connected via ${transport}`);
        isConnected.value = true;
        error.value = null;
        // Request initial state
        socket.emit("request_state");
    });

    socket.on("disconnect", () => {
        console.log("WebSocket disconnected");
        isConnected.value = false;
    });

    socket.on("connect_error", (err) => {
        console.error("WebSocket connection error:", err);
        isConnected.value = false;
        error.value = "Failed to connect to RetroBoard server";
    });

    socket.on("reconnect_attempt", (attemptNumber) => {
        console.log(`Reconnection attempt ${attemptNumber}...`);
    });

    socket.on("reconnect", (attemptNumber) => {
        console.log(`Reconnected after ${attemptNumber} attempts`);
        isConnected.value = true;
        error.value = null;
    });

    socket.on("reconnect_failed", () => {
        console.error("Failed to reconnect to server");
        error.value = "Unable to reconnect to RetroBoard server";
    });

    // Listen for app list updates
    socket.on("apps_list", (data) => {
        availableApps.value = data.apps;
        currentApp.value = data.current;
    });

    // Listen for current app changes
    socket.on("current_app", (data) => {
        // Only update config if app changed
        if (data.app !== lastKnownApp.value) {
            lastKnownApp.value = data.app;
            currentApp.value = data.app;
            if (data.config) {
                updateConfigFromServer(data.app, data.config);
            }
        } else {
            // Just update the current app name
            currentApp.value = data.app;
        }
    });

    // Listen for settings changes
    socket.on("settings", (data) => {
        if (data.brightness !== undefined) {
            brightness.value = data.brightness;
        }
    });

    // Listen for carousel config changes
    socket.on("carousel_config", (data) => {
        carouselEnabled.value = data.enabled || false;
        carouselApps.value = data.apps || [];
    });
}

// API Functions (still used for POST requests)
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
        // Save config for the app (current or not)
        const saveResponse = await fetch(
            `${API_BASE}/apps/${selectedApp.value}/config`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(config),
            },
        );

        if (!saveResponse.ok) {
            const data = await saveResponse.json();
            error.value = data.error || "Failed to save config";
            return;
        }

        // If it's not the current app, switch to it
        if (!isUpdatingCurrentApp) {
            const switchResponse = await fetch(`${API_BASE}/switch`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    app: selectedApp.value,
                }),
            });

            if (switchResponse.ok) {
                currentApp.value = selectedApp.value;
                lastKnownApp.value = selectedApp.value;
                error.value = null;
            } else {
                const data = await switchResponse.json();
                error.value = data.error || "Failed to switch app";
            }
        } else {
            // Config was saved and applied to current app
            error.value = null;
        }
    } catch (err) {
        error.value = "Failed to communicate with server";
        console.error("Error switching/updating app:", err);
    }
}

async function saveConfig() {
    if (!selectedApp.value) return;

    const config = getAppConfig(selectedApp.value);

    try {
        const response = await fetch(
            `${API_BASE}/apps/${selectedApp.value}/config`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(config),
            },
        );

        if (response.ok) {
            error.value = null;
        } else {
            const data = await response.json();
            error.value = data.error || "Failed to save config";
        }
    } catch (err) {
        error.value = "Failed to communicate with server";
        console.error("Error saving config:", err);
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

async function selectApp(app) {
    selectedApp.value = app;

    // Fetch saved config for this app from server
    try {
        const response = await fetch(`${API_BASE}/apps/${app}/config`);
        if (response.ok) {
            const data = await response.json();
            // Update form with saved config if it exists
            if (data.config && Object.keys(data.config).length > 0) {
                updateConfigFromServer(app, data.config);
            }
        }
    } catch (err) {
        console.error(`Error fetching config for ${app}:`, err);
        // Keep defaults if fetch fails
    }
}

async function fetchSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings`);
        if (response.ok) {
            const data = await response.json();
            brightness.value = data.brightness || 100;
        }
    } catch (err) {
        console.error("Error fetching settings:", err);
    }
}

async function updateBrightness() {
    try {
        const response = await fetch(`${API_BASE}/settings`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                brightness: brightness.value,
            }),
        });

        if (response.ok) {
            error.value = null;
        } else {
            const data = await response.json();
            error.value = data.error || "Failed to update brightness";
        }
    } catch (err) {
        error.value = "Failed to update settings";
        console.error("Error updating brightness:", err);
    }
}

async function fetchCarousel() {
    try {
        const response = await fetch(`${API_BASE}/carousel`);
        if (response.ok) {
            const data = await response.json();
            carouselEnabled.value = data.enabled || false;
            carouselApps.value = data.apps || [];
        }
    } catch (err) {
        console.error("Error fetching carousel config:", err);
    }
}

function requestStateUpdate() {
    if (socket && socket.connected) {
        socket.emit("request_state");
    }
}

async function updateCarousel() {
    try {
        const response = await fetch(`${API_BASE}/carousel`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                enabled: carouselEnabled.value,
                apps: carouselApps.value,
            }),
        });

        if (response.ok) {
            error.value = null;
            editingCarousel.value = false;
        } else {
            const data = await response.json();
            error.value = data.error || "Failed to update carousel";
        }
    } catch (err) {
        error.value = "Failed to update carousel";
        console.error("Error updating carousel:", err);
    }
}

function addCarouselApp() {
    if (availableApps.value.length === 0) return;

    carouselApps.value.push({
        app: availableApps.value[0],
        duration: 10,
    });
}

function removeCarouselApp(index) {
    carouselApps.value.splice(index, 1);
}

function toggleCarouselEdit() {
    editingCarousel.value = !editingCarousel.value;
    if (!editingCarousel.value) {
        // Cancelled editing, reload from server
        fetchCarousel();
    }
}

// Lifecycle
onMounted(async () => {
    // Load theme preference
    const savedTheme = localStorage.getItem("retroboard-theme");
    if (savedTheme) {
        isDarkTheme.value = savedTheme === "dark";
    }

    // Initialize WebSocket connection
    initializeWebSocket();

    // Fallback: fetch initial state via REST if WebSocket takes time to connect
    await fetchApps();
    await fetchSettings();
    await fetchCarousel();

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
});

onUnmounted(() => {
    // Disconnect WebSocket when component unmounts
    if (socket) {
        socket.disconnect();
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
                            @click="requestStateUpdate"
                            class="btn btn-secondary"
                            :disabled="!isConnected"
                            title="Refresh state from server"
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
                    <button
                        v-if="selectedApp === currentApp"
                        @click="switchApp"
                        class="btn btn-primary"
                    >
                        Update Config
                    </button>
                    <div v-else class="button-group">
                        <button @click="saveConfig" class="btn btn-secondary">
                            Save Config
                        </button>
                        <button @click="switchApp" class="btn btn-primary">
                            Switch to App
                        </button>
                    </div>
                </div>
            </section>

            <!-- Carousel/Rotation Mode -->
            <section class="carousel">
                <h2>🔄 Carousel Mode</h2>
                <div v-if="!editingCarousel" class="carousel-display">
                    <div class="carousel-status">
                        <span
                            class="status-badge"
                            :class="{ active: carouselEnabled }"
                        >
                            {{ carouselEnabled ? "Enabled" : "Disabled" }}
                        </span>
                        <span
                            v-if="carouselEnabled && carouselApps.length > 0"
                            class="carousel-info"
                        >
                            Rotating through {{ carouselApps.length }} app{{
                                carouselApps.length !== 1 ? "s" : ""
                            }}
                        </span>
                    </div>
                    <div v-if="carouselApps.length > 0" class="carousel-list">
                        <div
                            v-for="(item, index) in carouselApps"
                            :key="index"
                            class="carousel-item"
                        >
                            <span class="carousel-item-number"
                                >{{ index + 1 }}.</span
                            >
                            <span class="carousel-item-app">{{
                                formatAppName(item.app)
                            }}</span>
                            <span class="carousel-item-duration"
                                >{{ item.duration }}s</span
                            >
                        </div>
                    </div>
                    <button
                        @click="toggleCarouselEdit"
                        class="btn btn-secondary"
                    >
                        Configure Carousel
                    </button>
                </div>

                <div v-else class="carousel-editor">
                    <div class="form-group">
                        <label>
                            <input type="checkbox" v-model="carouselEnabled" />
                            Enable Carousel Mode
                        </label>
                    </div>

                    <div
                        v-if="carouselApps.length > 0"
                        class="carousel-apps-list"
                    >
                        <div
                            v-for="(item, index) in carouselApps"
                            :key="index"
                            class="carousel-app-config"
                        >
                            <div class="carousel-app-row">
                                <span class="carousel-app-number"
                                    >{{ index + 1 }}.</span
                                >
                                <select
                                    v-model="item.app"
                                    class="input carousel-app-select"
                                >
                                    <option
                                        v-for="app in availableApps"
                                        :key="app"
                                        :value="app"
                                    >
                                        {{ formatAppName(app) }}
                                    </option>
                                </select>
                                <input
                                    type="number"
                                    v-model.number="item.duration"
                                    min="1"
                                    max="3600"
                                    class="input carousel-duration-input"
                                    placeholder="Duration (s)"
                                />
                                <button
                                    @click="removeCarouselApp(index)"
                                    class="btn-remove"
                                    title="Remove"
                                >
                                    ❌
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="carousel-actions">
                        <button
                            @click="addCarouselApp"
                            class="btn btn-secondary"
                        >
                            ➕ Add App
                        </button>
                        <div class="button-group">
                            <button
                                @click="toggleCarouselEdit"
                                class="btn btn-secondary"
                            >
                                Cancel
                            </button>
                            <button
                                @click="updateCarousel"
                                class="btn btn-primary"
                            >
                                Save Carousel
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Settings -->
            <section class="settings">
                <h2>⚙️ Settings</h2>
                <div class="settings-form">
                    <div class="form-group">
                        <label> Brightness: {{ brightness }}% </label>
                        <input
                            type="range"
                            v-model.number="brightness"
                            @input="updateBrightness"
                            min="0"
                            max="100"
                            class="slider"
                        />
                        <div class="brightness-labels">
                            <span>0%</span>
                            <span>50%</span>
                            <span>100%</span>
                        </div>
                    </div>
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

.settings-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.slider {
    width: 100%;
    height: 0.5rem;
    border-radius: 0.25rem;
    background: #d1d5db;
    outline: none;
    cursor: pointer;
    -webkit-appearance: none;
}

.dark-theme .slider {
    background: #374151;
}

.slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
    background: #5568d3;
    transform: scale(1.1);
}

.dark-theme .slider::-webkit-slider-thumb {
    background: #818cf8;
}

.dark-theme .slider::-webkit-slider-thumb:hover {
    background: #6366f1;
}

.slider::-moz-range-thumb {
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
}

.slider::-moz-range-thumb:hover {
    background: #5568d3;
    transform: scale(1.1);
}

.dark-theme .slider::-moz-range-thumb {
    background: #818cf8;
}

.dark-theme .slider::-moz-range-thumb:hover {
    background: #6366f1;
}

.brightness-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.dark-theme .brightness-labels {
    color: #9ca3af;
}

.button-group {
    display: flex;
    gap: 1rem;
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

/* Carousel Styles */
.carousel-display {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.carousel-status {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 0.375rem;
    font-weight: 600;
    font-size: 0.875rem;
    background: #e5e7eb;
    color: #6b7280;
}

.status-badge.active {
    background: #d1fae5;
    color: #065f46;
}

.dark-theme .status-badge {
    background: #374151;
    color: #9ca3af;
}

.dark-theme .status-badge.active {
    background: #065f46;
    color: #d1fae5;
}

.carousel-info {
    color: #6b7280;
    font-size: 0.875rem;
}

.dark-theme .carousel-info {
    color: #9ca3af;
}

.carousel-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
}

.dark-theme .carousel-list {
    background: #1f2937;
    border-color: #374151;
}

.carousel-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: white;
    border-radius: 0.375rem;
    border: 1px solid #e5e7eb;
}

.dark-theme .carousel-item {
    background: #111827;
    border-color: #4b5563;
}

.carousel-item-number {
    font-weight: 600;
    color: #6b7280;
    min-width: 1.5rem;
}

.dark-theme .carousel-item-number {
    color: #9ca3af;
}

.carousel-item-app {
    flex: 1;
    font-weight: 500;
    color: #1f2937;
}

.dark-theme .carousel-item-app {
    color: #e5e7eb;
}

.carousel-item-duration {
    padding: 0.25rem 0.5rem;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.dark-theme .carousel-item-duration {
    background: #312e81;
    color: #c7d2fe;
}

.carousel-editor {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.carousel-apps-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.carousel-app-config {
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
}

.dark-theme .carousel-app-config {
    background: #1f2937;
    border-color: #374151;
}

.carousel-app-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.carousel-app-number {
    font-weight: 600;
    color: #6b7280;
    min-width: 1.5rem;
}

.dark-theme .carousel-app-number {
    color: #9ca3af;
}

.carousel-app-select {
    flex: 1;
}

.carousel-duration-input {
    width: 8rem;
}

.btn-remove {
    padding: 0.5rem;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 1rem;
    border-radius: 0.375rem;
    transition: all 0.2s;
}

.btn-remove:hover {
    background: #fee2e2;
    transform: scale(1.1);
}

.dark-theme .btn-remove:hover {
    background: #7f1d1d;
}

.carousel-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
</style>
