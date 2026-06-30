<template>
  <div v-if="dataLoaded && nodeSpatialRead" class="listbox-wrapper">
    <generic-node-settings
      :model-value="nodeSpatialRead"
      @update:model-value="handleGenericSettingsUpdate"
      @request-save="saveSettings"
    >
      <div class="listbox-wrapper">
        <div class="file-path-row">
          <el-input
            v-model="pathInput"
            placeholder="Path to .shp, .geojson, or .parquet"
            clearable
            class="file-path-input"
            @change="
              (val: string) => {
                handleManualPathChange(val);
                saveSettings();
              }
            "
          >
            <template #prefix>
              <i class="fas fa-globe" style="font-size: 14px" />
            </template>
          </el-input>
          <el-button title="Browse files" @click="modalVisibleForOpen = true">
            <span class="material-icons" style="font-size: 16px; line-height: 1">folder_open</span>
          </el-button>
        </div>
      </div>
      <div v-if="receivedTable" class="listbox-wrapper">
        <div class="listbox-subtitle">File Info</div>
        <div class="file-info-row">
          <span class="file-info-label">Type:</span>
          <span class="file-info-value">{{ receivedTable.file_type }}</span>
        </div>
      </div>

      <el-dialog
        v-model="modalVisibleForOpen"
        title="Select a spatial file"
        width="70%"
        append-to-body
        :close-on-click-modal="false"
      >
        <file-browser
          :allowed-file-types="['shp', 'geojson', 'json', 'parquet']"
          mode="open"
          context="dataFiles"
          :is-visible="modalVisibleForOpen"
          @file-selected="handleFileChange"
        />
      </el-dialog>
    </generic-node-settings>
  </div>
  <code-loader v-else />
</template>

<script lang="ts" setup>
import { CodeLoader } from "vue-content-loader";
import { ref } from "vue";
import { useNodeStore } from "../../../../../stores/node-store";
import { useNodeSettings } from "../../../../../composables/useNodeSettings";
import FileBrowser from "../../../../common/FileBrowser/fileBrowser.vue";
import { FileInfo } from "../../../../common/FileBrowser/types";
import GenericNodeSettings from "../../../baseNode/genericNodeSettings.vue";
import type { NodeBase, ReceivedTable } from "../../../baseNode/nodeInput";

interface NodeSpatialRead extends NodeBase {
  received_file: ReceivedTable;
}

const nodeStore = useNodeStore();
const nodeSpatialRead = ref<null | NodeSpatialRead>(null);
const receivedTable = ref<ReceivedTable | null>(null);
const dataLoaded = ref(false);
const modalVisibleForOpen = ref(false);
const pathInput = ref("");

const { saveSettings, pushNodeData, handleGenericSettingsUpdate } = useNodeSettings({
  nodeRef: nodeSpatialRead,
  onBeforeSave: () => {
    if (!nodeSpatialRead.value || !receivedTable.value) return false;
    nodeSpatialRead.value.received_file = receivedTable.value;
    return true;
  },
});

type GeoFileType = "shapefile" | "geoparquet" | "geojson";

function detectFileType(path: string): GeoFileType {
  const lower = path.toLowerCase();
  if (lower.endsWith(".shp")) return "shapefile";
  if (lower.endsWith(".geojson") || lower.endsWith(".json")) return "geojson";
  if (lower.endsWith(".parquet")) return "geoparquet";
  return "geojson";
}

function handleFileChange(file: FileInfo) {
  modalVisibleForOpen.value = false;
  const fileType = detectFileType(file.path);
  pathInput.value = file.path;

  const newReceivedFile: ReceivedTable = {
    path: file.path,
    file_type: fileType,
    name: file.name,
    table_settings: { file_type: fileType } as any,
  };

  receivedTable.value = newReceivedFile;
  if (nodeSpatialRead.value) {
    nodeSpatialRead.value.received_file = newReceivedFile;
    saveSettings();
  }
}

function handleManualPathChange(val: string) {
  if (!val || !nodeSpatialRead.value) return;
  const fileType = detectFileType(val);

  const newReceivedFile: ReceivedTable = {
    path: val,
    file_type: fileType,
    name: val.split(/[\\/]/).pop() || val,
    table_settings: { file_type: fileType } as any,
  };

  receivedTable.value = newReceivedFile;
  nodeSpatialRead.value.received_file = newReceivedFile;
}

async function loadNodeData(nodeId: number) {
  const nodeResult = await nodeStore.getNodeData(nodeId, false);
  if (nodeResult && nodeResult.setting_input) {
    nodeSpatialRead.value = nodeResult.setting_input as unknown as NodeSpatialRead;
    receivedTable.value = nodeSpatialRead.value?.received_file || null;
    pathInput.value = receivedTable.value?.path || "";
  } else {
    // Fresh node with no settings yet — bootstrap defaults
    nodeSpatialRead.value = {
      flow_id: nodeStore.flow_id,
      node_id: nodeId,
      cache_results: false,
      pos_x: 0,
      pos_y: 0,
      received_file: {
        path: "",
        file_type: "geojson",
        table_settings: { file_type: "geojson" },
      },
    } as unknown as NodeSpatialRead;
    receivedTable.value = null;
  }
  dataLoaded.value = true;
}

defineExpose({ loadNodeData, pushNodeData });
</script>

<style scoped>
.file-path-row {
  display: flex;
  gap: 4px;
  align-items: center;
}
.file-path-input {
  flex: 1;
}
.file-info-row {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}
.file-info-label {
  font-weight: 600;
  color: #666;
}
.file-info-value {
  color: #333;
}
</style>
