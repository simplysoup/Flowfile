<template>
  <div v-if="dataLoaded && nodeBufferGeometry" class="listbox-wrapper">
    <generic-node-settings
      :model-value="nodeBufferGeometry"
      @update:model-value="handleGenericSettingsUpdate"
      @request-save="saveSettings"
    >
      <div class="listbox-wrapper">
        <div class="listbox-subtitle">Buffer Settings</div>

        <div class="setting-row">
          <span class="setting-label">Geometry Column:</span>
          <el-input v-model="nodeBufferGeometry.geom_col" @change="saveSettings" />
        </div>

        <div class="setting-row">
          <span class="setting-label">Distance:</span>
          <el-input-number
            v-model="nodeBufferGeometry.distance"
            :step="0.001"
            :precision="6"
            :min="0"
            @change="saveSettings"
          />
        </div>

        <div class="setting-row">
          <span class="setting-label">Resolution:</span>
          <el-input-number
            v-model="nodeBufferGeometry.resolution"
            :step="1"
            :min="1"
            :max="64"
            @change="saveSettings"
          />
        </div>
      </div>
    </generic-node-settings>
  </div>
  <code-loader v-else />
</template>

<script lang="ts" setup>
import { CodeLoader } from "vue-content-loader";
import { ref } from "vue";
import { useNodeStore } from "../../../../../stores/node-store";
import { useNodeSettings } from "../../../../../composables/useNodeSettings";
import GenericNodeSettings from "../../../baseNode/genericNodeSettings.vue";
import type { NodeSingleInput } from "../../../baseNode/nodeInput";

interface NodeBufferGeometry extends NodeSingleInput {
  geom_col: string;
  distance: number;
  resolution: number;
}

const nodeStore = useNodeStore();
const nodeBufferGeometry = ref<null | NodeBufferGeometry>(null);
const dataLoaded = ref(false);

const { saveSettings, pushNodeData, handleGenericSettingsUpdate } = useNodeSettings({
  nodeRef: nodeBufferGeometry,
});

async function loadNodeData(nodeId: number) {
  const nodeResult = await nodeStore.getNodeData(nodeId, false);
  if (nodeResult) {
    nodeBufferGeometry.value = nodeResult.setting_input as unknown as NodeBufferGeometry;
    dataLoaded.value = true;
  }
}

defineExpose({ loadNodeData, pushNodeData });
</script>

<style scoped>
.setting-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}
.setting-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  min-width: 140px;
}
</style>
