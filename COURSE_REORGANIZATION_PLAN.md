# Course Reorganization Plan: GEOG 288KC Applications Course

## Overview

This document outlines the plan to reorganize GEOG 288KC from its current structure to an **applications-focused course** centered on **TerraTorch + PyTorch Lightning workflows**. The goal is to teach students practical geoAI application development using high-level libraries, introducing theory progressively as workflows increase in complexity.

---

## Guiding Principles

1. **TerraTorch + Lightning First**: All workflows use TerraTorch and PyTorch Lightning as primary interfaces
2. **Minimal Custom Code**: Avoid DIY implementations unless essential for teaching a specific concept
3. **Progressive Theory**: Introduce conceptual content in stages, tied to specific workflows
4. **Application Priority**: Deliver working application workflows; theory supports practice
5. **Quarto Format**: Maintain Quarto as the primary authoring format

---

## Preservation of Current Materials

Before reorganization, the current course materials are preserved in a separate branch:

- **Branch**: `claude/geogfm-course-materials-GNJEA` ✅ Pushed to origin
- **Purpose**: Future "from-scratch" course development
- **Contains**: Full geogfm package, DIY implementations, current chapter structure

---

## New Course Structure

### Phase 1: Foundations (Weeks 0-1)

#### Week 0: Course Introduction & Environment Setup
**Focus**: Getting started, ecosystem overview

| Content | Type | Source |
|---------|------|--------|
| Course overview and objectives | New | Create from syllabus |
| UCSB AI Sandbox setup | Keep | Existing setup guides |
| TerraTorch/TorchGeo ecosystem introduction | Refactor | From c03a-terratorch-foundations |
| What are foundation models? (brief) | Refactor | Condense from c00a/c00b |

**Theory Introduced**:
- What foundation models are and why they matter for geospatial applications
- Brief architecture overview (enough to understand inputs/outputs)

---

#### Week 1: Data Access & TerraTorch Basics
**Focus**: Working with geospatial data through TorchGeo/TerraTorch

| Content | Type | Source |
|---------|------|--------|
| STAC API data discovery | Keep | c01-geospatial-data-foundations |
| TorchGeo datasets and dataloaders | Refactor | From c01 + cheatsheets |
| TerraTorch data configuration | Refactor | From terratorch_finetuning_workflow |
| Loading pretrained models | Refactor | From c04-pretraining-implementation |

**Theory Introduced**:
- Data normalization for remote sensing
- Patch-based processing concepts

---

### Phase 2: Core Application Workflows (Weeks 2-7)

#### Week 2: Embedding Analysis
**Focus**: Understanding what foundation models learn through feature extraction

| Content | Type | Source |
|---------|------|--------|
| Feature extraction with TerraTorch | New | Develop workflow |
| Embedding visualization (UMAP, t-SNE) | Refactor | From c04-pretraining-implementation |
| Similarity search and retrieval | New | Develop workflow |
| Comparing embeddings across models | New | Develop workflow |

**Theory Introduced**:
- Latent representations and feature spaces
- Why pretrained features are useful

**Practical Application**:
- Scene similarity search
- Anomaly detection via embeddings

---

#### Week 3: Mask/Gap Filling
**Focus**: Using masked autoencoders for reconstruction tasks

| Content | Type | Source |
|---------|------|--------|
| Masked Autoencoder concepts | Refactor | From c00a + c04 |
| Cloud gap filling workflow | New | Develop with TerraTorch |
| Missing data reconstruction | New | Develop workflow |
| Temporal gap filling | Refactor | From c06 temporal content |

**Theory Introduced**:
- Masked image modeling
- Self-supervised learning basics
- Attention mechanisms (brief, visual)

**Practical Application**:
- Cloud removal from Sentinel-2 imagery
- Filling missing pixels in time series

---

#### Week 4: Next Image Prediction
**Focus**: Temporal modeling and forecasting

| Content | Type | Source |
|---------|------|--------|
| Temporal data handling in TorchGeo | Refactor | From c02 + c06 |
| Temporal encodings | Refactor | From ndvi_timeseries_forecasting |
| Forecasting with foundation models | New | Develop workflow |
| NDVI/vegetation index prediction | Refactor | From ndvi_timeseries_forecasting |

**Theory Introduced**:
- Temporal positional encodings
- Sequence modeling concepts
- Autoregressive vs. direct prediction

**Practical Application**:
- NDVI time series forecasting
- Seasonal pattern prediction

**Deliverable**: Project Proposal Due

---

#### Week 5: Classification
**Focus**: Scene and image classification workflows

| Content | Type | Source |
|---------|------|--------|
| Classification with TerraTorch | Refactor | From c03a-terratorch-foundations |
| Linear probing workflow | Refactor | From c05-training-loop-optimization |
| Full fine-tuning workflow | Refactor | From terratorch_finetuning_workflow |
| Multi-label classification | New | Develop workflow |

**Theory Introduced**:
- Transfer learning and fine-tuning strategies
- When to use linear probing vs. full fine-tuning
- Classification heads and loss functions

**Practical Application**:
- Land cover classification (EuroSAT)
- Multi-label scene tagging

---

#### Week 6: Object Detection
**Focus**: Detecting objects in satellite imagery

| Content | Type | Source |
|---------|------|--------|
| Object detection concepts | Refactor | From object_detection.qmd |
| Detection with TerraTorch/TorchGeo | Refactor | From examples |
| Bounding box annotation workflows | New | Develop workflow |
| Detection evaluation metrics | Refactor | From model_evaluation_validation cheatsheet |

**Theory Introduced**:
- Detection architectures (brief: anchors, feature pyramids)
- Non-maximum suppression
- mAP and IoU metrics

**Practical Application**:
- Vehicle/building detection
- Infrastructure mapping

---

#### Week 7: Semantic Segmentation
**Focus**: Pixel-wise classification workflows

| Content | Type | Source |
|---------|------|--------|
| Segmentation with TerraTorch | Refactor | From segmentation_tutorial.qmd |
| Segmentation fine-tuning | Refactor | From segmentation_finetuning.ipynb |
| Tiling and stitching for large images | Refactor | From tiling-and-patches.qmd |
| Segmentation evaluation | Refactor | From existing materials |

**Theory Introduced**:
- Encoder-decoder architectures (brief)
- Dense prediction concepts
- Spatial resolution considerations

**Practical Application**:
- Land cover segmentation
- Change detection via segmentation

**Deliverable**: Initial MVP Due

---

### Phase 3: Project Development & Synthesis (Weeks 8-10)

#### Week 8: Integration & Scaling
**Focus**: Combining workflows, scaling to production

| Content | Type | Source |
|---------|------|--------|
| Combining multiple workflows | New | Develop |
| Scaling inference (batch processing) | Refactor | From c09-model-implementation-deployment |
| Lightning optimization techniques | New | Develop |
| Checkpoint management | Refactor | From existing |

**Theory Introduced**:
- Efficient inference strategies
- Model optimization basics

---

#### Week 9: Deployment & APIs
**Focus**: Making models accessible

| Content | Type | Source |
|---------|------|--------|
| Model export and deployment | Refactor | From c09 |
| Simple API development | New | Develop |
| Gradio/Streamlit demos | New | Develop |
| HuggingFace Hub integration | Refactor | From existing stubs |

---

#### Week 10: Project Presentations & Synthesis
**Focus**: Final presentations and course synthesis

| Content | Type | Source |
|---------|------|--------|
| Course synthesis | Refactor | From c10 |
| Best practices summary | New | Develop |
| Future directions | Refactor | From c10 |

**Deliverable**: Final Project Presentations

---

## New Navigation Structure

```
GEOG 288KC (navbar)
├── Home
├── Syllabus
├── Weekly Sessions
│   ├── Week 0: Introduction & Setup
│   ├── Week 1: Data Access & TerraTorch Basics
│   ├── Week 2: Embedding Analysis
│   ├── Week 3: Mask/Gap Filling
│   ├── Week 4: Next Image Prediction
│   ├── Week 5: Classification
│   ├── Week 6: Object Detection
│   ├── Week 7: Segmentation
│   ├── Week 8: Integration & Scaling
│   ├── Week 9: Deployment & APIs
│   └── Week 10: Presentations
├── Cheatsheets (reorganized by workflow)
├── Conceptual Guides (theory references)
├── Project Templates
└── Resources
```

---

## File Naming Convention

New chapter files will follow the pattern:
- `w00-introduction-setup.qmd`
- `w01-data-access-terratorch-basics.qmd`
- `w02-embedding-analysis.qmd`
- `w03-mask-gap-filling.qmd`
- `w04-next-image-prediction.qmd`
- `w05-classification.qmd`
- `w06-object-detection.qmd`
- `w07-segmentation.qmd`
- `w08-integration-scaling.qmd`
- `w09-deployment-apis.qmd`
- `w10-presentations-synthesis.qmd`

---

## Implementation Phases

### Phase A: Preparation
1. Push preservation branch to origin
2. Create new chapter file structure
3. Update `_quarto.yml` navigation

### Phase B: Core Content Development (Weeks 0-7)
1. Refactor existing content for Weeks 0-1
2. Develop new workflow content for Weeks 2-7
3. Update cheatsheets to align with new structure

### Phase C: Project & Deployment Content (Weeks 8-10)
1. Develop integration and scaling content
2. Create deployment/API materials
3. Update project templates

### Phase D: Polish & Testing
1. Test all code examples
2. Verify build process
3. Update CLAUDE.md and documentation

---

## Success Criteria

1. Students can complete each weekly application workflow using TerraTorch/Lightning
2. Theory is introduced progressively and tied to practical applications
3. Minimal custom code; high-level library usage throughout
4. All code examples are production-ready and reusable
5. Clear progression from simple (embeddings) to complex (segmentation) workflows

---

## Dependencies & Prerequisites

### Technical Stack
- TerraTorch (latest stable)
- PyTorch Lightning
- TorchGeo
- rasterio, xarray, pystac-client
- UCSB AI Sandbox environment

### Student Prerequisites
- Python programming experience
- Basic understanding of remote sensing data
- Familiarity with PyTorch (helpful but not required)

---

## Research Findings & Decisions

### TerraTorch Capability Assessment (2025-12-19)

| Workflow | TerraTorch Support | Status | Notes |
|----------|-------------------|--------|-------|
| Embedding Analysis | Supported | Ready | Feature extraction works well |
| Mask/Gap Filling | Partial | Needs wrapper | Prithvi has `inference.py` for reconstruction; custom mask requires forward function modification |
| Next Image Prediction | Supported | Ready | `PixelWiseRegressionTask` + `expand_temporal_dimension` |
| Classification | Fully Supported | Ready | `ClassificationTask` |
| Object Detection | Under Development | **FLAG** | In development branch with known issues; existing course material requires extensive custom code |
| Segmentation | Fully Supported | Ready | `SemanticSegmentationTask` |

### Key Sources
- [TerraTorch Documentation](https://ibm.github.io/terratorch/stable/)
- [TerraTorch Examples (Blumenstiel)](https://github.com/blumenstiel/TerraTorch-Examples)
- [Prithvi-EO-2.0 Paper](https://arxiv.org/html/2412.02732v1)
- [Cloud Gap Imputation Paper](https://arxiv.org/abs/2404.19609)
- [TorchGeo ObjectDetectionTask](https://github.com/microsoft/torchgeo/blob/main/torchgeo/trainers/detection.py)

---

## Resolved Questions

1. **Project Milestones**: ✅ **RESOLVED** - Proposals move to Week 4 (was Week 5)

2. **geogfm Package**: ✅ **RESOLVED** - Fully deprecate; preserve in `geogfm-course-materials` branch for future "from-scratch" course

3. **Mask/Gap Filling (Week 3)**: ✅ **RESOLVED** - Use Prithvi's native reconstruction via `inference.py` with minimal wrapper. Acceptable for teaching since it demonstrates a real workflow.

4. **Next Image Prediction (Week 4)**: ✅ **RESOLVED** - Well-supported via `PixelWiseRegressionTask` with `expand_temporal_dimension`. Existing `ndvi_timeseries_forecasting.qmd` is a good starting point.

5. **Object Detection (Week 6)**: ✅ **RESOLVED** - Use TorchGeo's `ObjectDetectionTask` directly (supports faster-rcnn, fcos, retinanet). Maintains Lightning-based workflow while TerraTorch detection matures.

---

## Updated Deliverables Timeline

| Week | Deliverable |
|------|-------------|
| Week 4 | **Project Proposal Due** (moved from Week 5) |
| Week 7 | Initial MVP Due |
| Week 10 | Final Project Presentations |

---

*Document created: 2025-12-19*
*Last updated: 2025-12-19*
