# Materials Tracking: GEOG 288KC Reorganization

This document tracks all materials for the course reorganization, categorized by action required.

---

## Legend

- **Status**: `TODO` | `IN_PROGRESS` | `DONE` | `BLOCKED`
- **Priority**: `HIGH` (core workflow) | `MEDIUM` (supporting) | `LOW` (nice-to-have)

---

## 1. NEW MATERIALS TO DEVELOP

Materials that need to be created from scratch or significantly expanded.

### Week 0: Introduction & Setup

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w00-introduction-setup.qmd` | Course overview, objectives, ecosystem introduction | HIGH | TODO | Combine syllabus intro with TerraTorch ecosystem overview |
| TerraTorch ecosystem diagram | Visual showing TorchGeo/TerraTorch/Lightning stack | MEDIUM | TODO | Create clear architecture diagram |

### Week 2: Embedding Analysis

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w02-embedding-analysis.qmd` | Feature extraction and embedding workflows | HIGH | TODO | Core new workflow |
| Embedding extraction tutorial | Step-by-step TerraTorch feature extraction | HIGH | TODO | Show multiple models |
| Similarity search example | Find similar scenes using embeddings | MEDIUM | TODO | Practical application |
| Embedding comparison notebook | Compare embeddings across different GFMs | MEDIUM | TODO | Educational value |

### Week 3: Mask/Gap Filling

**NOTE**: Use Prithvi's native reconstruction via `inference.py`. Reference: [Cloud Gap Imputation Paper](https://arxiv.org/abs/2404.19609)

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w03-mask-gap-filling.qmd` | MAE reconstruction workflows | HIGH | TODO | Use Prithvi `inference.py` with minimal wrapper |
| Cloud gap filling tutorial | Using MAE for cloud removal | HIGH | TODO | Based on arxiv paper methodology |
| Missing data reconstruction | Filling temporal gaps | MEDIUM | TODO | Build on temporal content |
| MAE concepts explainer | Brief intro to masked autoencoders | MEDIUM | TODO | Theory component |

### Week 4: Next Image Prediction

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w04-next-image-prediction.qmd` | Temporal forecasting workflows | HIGH | TODO | Core new workflow |
| Vegetation forecasting tutorial | NDVI/EVI prediction | HIGH | TODO | Extend existing NDVI tutorial |
| Seasonal pattern prediction | Multi-step forecasting | MEDIUM | TODO | More advanced application |

### Week 6: Object Detection

**NOTE**: TerraTorch detection is under development with known issues. Use **TorchGeo's `ObjectDetectionTask`** instead.

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w06-object-detection.qmd` | Detection workflows using TorchGeo | HIGH | TODO | Use `ObjectDetectionTask` (faster-rcnn, fcos, retinanet) |
| TorchGeo detection tutorial | Step-by-step detection with Lightning | HIGH | TODO | DIOR or VHR10 dataset |
| Annotation workflow guide | How to prepare detection datasets | MEDIUM | TODO | Practical need |
| Detection concepts explainer | Anchors, NMS, mAP (brief) | MEDIUM | TODO | Theory component |

### Week 8: Integration & Scaling

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w08-integration-scaling.qmd` | Combining workflows, optimization | HIGH | TODO | New content |
| Multi-workflow pipeline | Example combining multiple workflows | MEDIUM | TODO | Show integration |
| Lightning optimization guide | Efficient training techniques | MEDIUM | TODO | Practical scaling |

### Week 9: Deployment & APIs

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `w09-deployment-apis.qmd` | Deployment and API development | HIGH | TODO | New content needed |
| Gradio demo tutorial | Building simple model demos | MEDIUM | TODO | Practical deployment |
| HuggingFace Hub guide | Publishing models to Hub | MEDIUM | TODO | Extend existing stubs |

### Cheatsheets (New)

| Material | Description | Priority | Status | Notes |
|----------|-------------|----------|--------|-------|
| `terratorch_embeddings.qmd` | Feature extraction quick reference | MEDIUM | TODO | Supports Week 2 |
| `mae_reconstruction.qmd` | MAE usage quick reference | MEDIUM | TODO | Supports Week 3 |
| `temporal_modeling.qmd` | Time series modeling reference | MEDIUM | TODO | Supports Week 4 |

---

## 2. MATERIALS TO REFACTOR/EDIT

Existing materials that need modification to fit the new structure.

### Week 0-1: Foundations

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `c00a-foundation_model_architectures.qmd` | Move to conceptual guides | Condense, remove implementation details | MEDIUM | TODO | Keep as reference |
| `c00b-introduction-to-deeplearning-architecture.qmd` | Move to conceptual guides | Condense for applications focus | MEDIUM | TODO | Keep as reference |
| `c01-geospatial-data-foundations.qmd` | `w01-data-access-terratorch-basics.qmd` | Refactor to focus on TorchGeo data loading | HIGH | TODO | Significant refactor |
| `c03a-terratorch-foundations.qmd` | Split: W0 intro + W1 data + W5 classification | Extract ecosystem intro for W0 | HIGH | TODO | Core content source |

### Week 4: Next Image Prediction

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `ndvi_timeseries_forecasting.qmd` | `w04-next-image-prediction.qmd` | Integrate and expand | HIGH | TODO | Good starting point |
| `c06-model-evaluation-analysis.qmd` | Extract temporal content | Move temporal modeling to W4 | MEDIUM | TODO | Preserve in branch first |

### Week 5: Classification

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `c03a-terratorch-foundations.qmd` | `w05-classification.qmd` | Extract classification workflow | HIGH | TODO | Core content |
| `c05-training-loop-optimization.qmd` | `w05-classification.qmd` | Extract fine-tuning strategies | HIGH | TODO | Keep transfer learning theory |
| `terratorch_finetuning_workflow.qmd` | `w05-classification.qmd` | Integrate workflow | HIGH | TODO | Primary workflow example |
| `c04-pretraining-implementation.qmd` | Split across weeks | Extract embedding analysis, feature comparison | MEDIUM | TODO | Useful content |

### Week 6: Object Detection

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `object_detection.qmd` | `w06-object-detection.qmd` | Major refactor for TerraTorch | HIGH | TODO | Need TerraTorch detection workflow |

### Week 7: Segmentation

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `segmentation_tutorial.qmd` | `w07-segmentation.qmd` | Refactor for TerraTorch focus | HIGH | TODO | Good content base |
| `segmentation_finetuning.ipynb` | Reference/example | Keep as supplementary | MEDIUM | TODO | Convert to .qmd if needed |
| `tiling-and-patches.qmd` | Integrate into W7 | Move tiling content to segmentation week | MEDIUM | TODO | Important for large images |

### Week 9: Deployment

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `c09-model-implementation-deployment.qmd` | `w09-deployment-apis.qmd` | Refactor, add API content | HIGH | TODO | Extend with Gradio/Streamlit |

### Week 10: Synthesis

| Current File | Target | Action | Priority | Status | Notes |
|--------------|--------|--------|----------|--------|-------|
| `c10-project-presentations-synthesis.qmd` | `w10-presentations-synthesis.qmd` | Light refactor | LOW | TODO | Mostly keep as-is |

### Cheatsheets (Refactor)

| Current File | Action | Priority | Status | Notes |
|--------------|--------|----------|--------|-------|
| `terratorch_model_zoo.qmd` | Update for new workflow focus | MEDIUM | TODO | Ensure current |
| `finetuning_basics.qmd` | Align with W5 classification | MEDIUM | TODO | Reference from W5 |
| `dataset_organization_terratorch.qmd` | Keep, ensure aligned | MEDIUM | TODO | Critical for data prep |
| `model_evaluation_validation.qmd` | Update metrics by workflow | MEDIUM | TODO | Reference across weeks |
| `torchgeo_basics.qmd` | Emphasize for W1 | MEDIUM | TODO | Core data loading |
| `loading_models.qmd` | Update for embedding focus | MEDIUM | TODO | Reference from W2 |

### Explainers (Refactor)

| Current File | Action | Priority | Status | Notes |
|--------------|--------|----------|--------|-------|
| `ai-ml-dl-fm-hierarchy.qmd` | Keep as conceptual reference | LOW | TODO | Move to Conceptual Guides section |
| `neural_networks_explainer.qmd` | Keep as reference | LOW | TODO | Move to Conceptual Guides |
| `geospatial-prediction-hierarchy.qmd` | Keep as reference | LOW | TODO | Useful taxonomy |

---

## 3. MATERIALS TO ARCHIVE/MOVE OUT

Materials that should be moved to the preservation branch or removed from main course.

### Move to `geogfm-course-materials` Branch

| File/Directory | Reason | Priority | Status | Notes |
|----------------|--------|----------|--------|-------|
| `geogfm/` (entire package) | "From scratch" course content | HIGH | TODO | Core of future course |
| `c02-spatial-temporal-attention-mechanisms.qmd` | Heavy DIY preprocessing | MEDIUM | TODO | Replace with TorchGeo approach |
| `c03-complete-gfm-architecture.qmd` | CNN from scratch training | MEDIUM | TODO | Replace with TerraTorch |
| Custom transformer implementations | DIY code | HIGH | TODO | Part of geogfm package |
| Tangled code modules (`c01.py`, `c02.py`, etc.) | DIY utilities | HIGH | TODO | Part of geogfm package |

### Remove or Deprecate

| File | Reason | Priority | Status | Notes |
|------|--------|----------|--------|-------|
| `resnet.qmd` | DIY ResNet implementation | LOW | TODO | Not needed for applications |
| `text_encoder.qmd` | Advanced topic, not core workflow | LOW | TODO | Could keep as extra |
| `tools/filters/tangle.py` | Not needed without geogfm | LOW | TODO | Remove after migration |

### Keep but Reorganize

| File | New Location | Priority | Status | Notes |
|------|--------------|----------|--------|-------|
| `normalization_comparison.qmd` | Extras/Advanced | LOW | TODO | Useful reference |
| `HLS_downloads.qmd` | Extras/Data Access | LOW | TODO | Specific data source |
| `terratorch_workflows.qmd` | Integrate into weekly content | MEDIUM | TODO | Good examples |
| `Terramind_EuroSAT.ipynb` | Extras/Examples | LOW | TODO | Supplementary |
| `TerraTorch_training_demo.ipynb` | Extras/Examples | LOW | TODO | Supplementary |

---

## 4. CONFIGURATION UPDATES

| File | Action | Priority | Status | Notes |
|------|--------|----------|--------|-------|
| `_quarto.yml` | Complete navigation restructure | HIGH | TODO | After content ready |
| `CLAUDE.md` | Update for new structure | HIGH | TODO | After content ready |
| `Syllabus.md` | Update weekly topics | HIGH | TODO | Align with new weeks |
| `environment.yml` | Verify TerraTorch/Lightning versions | MEDIUM | TODO | Ensure compatibility |
| `index.qmd` | Update course overview | MEDIUM | TODO | Reflect new focus |

---

## 5. DEPENDENCY VERIFICATION

Research completed 2025-12-19. Updated status:

| Dependency | Need | Status | Notes |
|------------|------|--------|-------|
| TerraTorch MAE reconstruction | Week 3 | **PARTIAL** | Prithvi has `inference.py` for reconstruction; custom mask needs forward function mod. Use Prithvi native reconstruction with minimal wrapper. |
| TerraTorch detection heads | Week 6 | **BLOCKED** | Under development in `obj_det_geobench` branch with known issues. Use TorchGeo `ObjectDetectionTask` instead. |
| TerraTorch temporal models | Week 4 | **READY** | `PixelWiseRegressionTask` + `expand_temporal_dimension` works. Prithvi has 3D temporal encodings. |
| TorchGeo detection datasets | Week 6 | **READY** | DIOR, VHR10 available. `ObjectDetectionTask` supports faster-rcnn, fcos, retinanet. |
| Lightning 2.x compatibility | All | TODO | Ensure examples work |
| TerraTorch ClassificationTask | Week 5 | **READY** | Fully supported |
| TerraTorch SegmentationTask | Week 7 | **READY** | Fully supported |

### Key Research Sources
- [TerraTorch Examples](https://github.com/blumenstiel/TerraTorch-Examples) - Sen1Floods11, Burn Scars, Multi-temporal Crop tutorials
- [Cloud Gap Imputation Paper](https://arxiv.org/abs/2404.19609) - Prithvi for gap filling
- [Prithvi-EO-2.0](https://arxiv.org/html/2412.02732v1) - 3D temporal/spatial embeddings
- [TerraTorch Issue #362](https://github.com/IBM/terratorch/issues/362) - Object detection data mismatch issues

---

## 6. IMPLEMENTATION ORDER

### Phase A: Preparation (Immediate)
1. [x] Push `geogfm-course-materials` branch to origin → `claude/geogfm-course-materials-GNJEA`
2. [ ] Create new chapter file structure (empty files)
3. [ ] Verify TerraTorch/Lightning dependencies

### Phase B: Core Weeks (Priority Order)
1. [ ] Week 1: Data Access & TerraTorch Basics
2. [ ] Week 5: Classification (most content exists)
3. [ ] Week 7: Segmentation (good existing content)
4. [ ] Week 2: Embedding Analysis
5. [ ] Week 0: Introduction & Setup
6. [ ] Week 3: Mask/Gap Filling
7. [ ] Week 4: Next Image Prediction
8. [ ] Week 6: Object Detection

### Phase C: Supporting Weeks
1. [ ] Week 8: Integration & Scaling
2. [ ] Week 9: Deployment & APIs
3. [ ] Week 10: Presentations & Synthesis

### Phase D: Polish
1. [ ] Update cheatsheets
2. [ ] Reorganize explainers
3. [ ] Update navigation and config
4. [ ] Full build and testing

---

## 7. REVIEW CHECKPOINTS

| Checkpoint | Content | Reviewer | Status |
|------------|---------|----------|--------|
| Plan Review | This document + reorganization plan | Instructor | PENDING |
| Week 0-1 Draft | Foundation content | Instructor | - |
| Weeks 2-4 Draft | Embedding, MAE, Temporal | Instructor | - |
| Weeks 5-7 Draft | Classification, Detection, Segmentation | Instructor | - |
| Weeks 8-10 Draft | Integration, Deployment, Synthesis | Instructor | - |
| Final Review | Complete course build | Instructor | - |

---

## 8. RESOLVED QUESTIONS

### Content Questions (Resolved via Research 2025-12-19)
1. **TerraTorch MAE**: ✅ Use Prithvi's native `inference.py` reconstruction with minimal wrapper. Custom mask support needs forward function modification but is acceptable for teaching.
2. **Detection Support**: ✅ TerraTorch detection is under development with issues. **Use TorchGeo's `ObjectDetectionTask`** (faster-rcnn, fcos, retinanet) for now.
3. **Temporal Models**: ✅ `PixelWiseRegressionTask` + `expand_temporal_dimension` works. Prithvi-EO-2.0 has 3D temporal embeddings.

### Structural Questions (Resolved via User Decision)
4. **Week Pacing**: ✅ Embedding analysis is substantial enough for a full week.
5. **Project Timeline**: ✅ **Proposals move to Week 4** (from Week 5).
6. **geogfm Package**: ✅ **Fully deprecate**. Preserve in `geogfm-course-materials` branch for future "from-scratch" course. Any needed utilities go in local .py files.

---

## 9. REMAINING ITEMS FOR FOLLOW-UP

### Object Detection Approach - RESOLVED
✅ **Decision**: Use TorchGeo's `ObjectDetectionTask` directly (faster-rcnn, fcos, retinanet with DIOR/VHR10 datasets)

### MEDIUM PRIORITY: Resource Questions
- **Datasets for Gap Filling**: Need to identify standard cloud-masked datasets for Week 3
- **Compute Requirements**: Verify that all workflows run on UCSB AI Sandbox

---

*Document created: 2025-12-19*
*Last updated: 2025-12-19*
