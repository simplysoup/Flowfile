<template>
  <div class="spatial-map-container">
    <div ref="mapContainer" class="spatial-map"></div>
    <div v-if="loading" class="spatial-map-overlay">
      <div class="spinner"></div>
      <span>Loading spatial preview...</span>
    </div>
    <div v-else-if="error" class="spatial-map-overlay spatial-map-error">
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";

interface Props {
  flowId: number;
  nodeId: number;
  geomCol?: string;
}

const props = withDefaults(defineProps<Props>(), {
  geomCol: "_flowfile_geom",
});

const mapContainer = ref<HTMLElement | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

let map: L.Map | null = null;
let geoJsonLayer: L.GeoJSON | null = null;

async function fetchAndRender() {
  loading.value = true;
  error.value = null;

  await nextTick();

  if (!mapContainer.value) {
    error.value = "Map container not available.";
    loading.value = false;
    return;
  }

  try {
    if (!map) {
      map = L.map(mapContainer.value).setView([0, 0], 2);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(map);
    }

    const response = await axios.get("/spatial/preview", {
      params: {
        flow_id: props.flowId,
        node_id: props.nodeId,
        geom_col: props.geomCol,
        max_polygons: 5000,
        tolerance: 0.001,
      },
    });

    const geojson = response.data;
    if (!geojson.features || geojson.features.length === 0) {
      error.value = "No geometry data available for this node.";
      loading.value = false;
      return;
    }

    if (geoJsonLayer) {
      map.removeLayer(geoJsonLayer);
    }

    geoJsonLayer = L.geoJSON(geojson, {
      style: {
        color: "#3388ff",
        weight: 2,
        opacity: 0.8,
        fillOpacity: 0.3,
      },
    }).addTo(map);

    const bounds = geoJsonLayer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  } catch (e: any) {
    error.value = e.message || "Failed to load spatial preview.";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchAndRender();
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});

watch(
  () => [props.flowId, props.nodeId, props.geomCol],
  () => {
    fetchAndRender();
  },
);
</script>

<style scoped>
.spatial-map-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
}

.spatial-map {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.spatial-map-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #666;
  background: rgba(255, 255, 255, 0.85);
  z-index: 1000;
}

.spatial-map-overlay .spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-top-color: #3388ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spatial-map-error {
  color: #e6553a;
  font-size: 13px;
}
</style>
