<template>
  <div v-if="dataLoaded && nodeSpatialJoin" class="listbox-wrapper">
    <generic-node-settings
      :model-value="nodeSpatialJoin"
      @update:model-value="handleGenericSettingsUpdate"
      @request-save="saveSettings"
    >
      <div class="listbox-wrapper">
        <div class="listbox-subtitle">Spatial Join Settings</div>

        <div class="setting-row">
          <span class="setting-label">Join Predicate:</span>
          <el-select v-model="nodeSpatialJoin.join_predicate" @change="saveSettings">
            <el-option label="Intersects" value="intersects" />
            <el-option label="Contains" value="contains" />
            <el-option label="Within" value="within" />
          </el-select>
        </div>

        <div class="setting-row">
          <span class="setting-label">Left Geometry Column:</span>
          <el-input v-model="nodeSpatialJoin.left_geom_col" @change="saveSettings" />
        </div>

        <div class="setting-row">
          <span class="setting-label">Right Geometry Column:</span>
          <el-input v-model="nodeSpatialJoin.right_geom_col" @change="saveSettings" />
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
import type { NodeMultiInput } from "../../../baseNode/nodeInput";

interface NodeSpatialJoin extends NodeMultiInput {
  join_predicate: "intersects" | "contains" | "within";
  left_geom_col: string;
  right_geom_col: string;
}

const nodeStore = useNodeStore();
const nodeSpatialJoin = ref<null | NodeSpatialJoin>(null);
const dataLoaded = ref(false);

const { saveSettings, pushNodeData, handleGenericSettingsUpdate } = useNodeSettings({
  nodeRef: nodeSpatialJoin,
});

async function loadNodeData(nodeId: number) {
  const nodeResult = await nodeStore.getNodeData(nodeId, false);
  if (nodeResult) {
    nodeSpatialJoin.value = nodeResult.setting_input as unknown as NodeSpatialJoin;
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
