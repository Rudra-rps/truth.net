# TruthNet MVP - Scope Freeze

**Date Locked:** December 25, 2025

## Supported Inputs
- ✅ **Video files** (primary)
- ✅ **Image files** (static analysis)
- ❌ **Audio** (optional stretch goal, not MVP)

## Agent Architecture for MVP

### Core Agents (Required)
1. **Visual Agent** ✅
   - Face detection and analysis
   - Frame sampling
   - Artifact detection (face warping, blending artifacts)
   - Stub ML models if needed

2. **Metadata Agent** ✅
   - EXIF parsing
   - Encoding history analysis
   - Timestamp validation
   - Provenance checking

### Stretch Goals (If Time Permits)
3. **Audio Agent** ❌
   - Spectrogram analysis
   - Voice consistency
   - Lip-sync detection

4. **Lip-sync Agent** ❌
   - Audio-visual synchronization
   - Mouth movement analysis

## Verdict System

### Risk Levels
- **Authentic** - High confidence real content
- **Suspicious** - Some anomalies detected
- **High-Risk** - Strong indicators of manipulation

### Scoring System
- Visual Agent weight: **45%**
- Metadata Agent weight: **55%**
- (Audio Agent weight: 30% - if implemented)

## Technical Decisions

### Communication
- **MVP:** Direct HTTP/JSON between services
- **Future:** gRPC for production (already on roadmap)

### Storage
- **MVP:** Local filesystem (`/tmp/media/{uuid}`)
- **Future:** S3/Cloud storage

### ML Models
- **MVP:** Rule-based heuristics + lightweight models
- **Future:** Full transformer models, ensemble learning

## Out of Scope for MVP
- Real-time processing
- Blockchain verification
- Social media integration
- Multi-user system
- Authentication/Authorization
- Production-grade storage
- Advanced ML models

## Success Criteria
✅ Upload a video/image
✅ Get a verdict with confidence score
✅ See clear explanations for the verdict
✅ View agent breakdown
✅ Demo-ready in 72 hours

---
**NO SCOPE CREEP BEYOND THIS DOCUMENT**
