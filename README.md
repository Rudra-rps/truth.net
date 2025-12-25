# TruthNet Monorepo

A multimodal AI platform combining visual, audio, and text processing with lip-sync synthesis.

## Project Structure

```
truthnet/
├── apps/
│   ├── api-go/                # Go backend (main entry point)
│   └── frontend/              # Next.js web interface
│
├── services/
│   ├── visual-agent/          # Python ML service for visual processing
│   ├── audio-agent/           # Audio processing service
│   ├── lipsync-agent/         # Lip-sync synthesis service
│   └── metadata-agent/        # Metadata management service
│
├── packages/
│   ├── proto/                 # gRPC protobuf definitions
│   └── shared/                # Shared schemas and utilities
│
├── infra/
│   ├── docker/                # Docker configurations
│   └── scripts/               # Infrastructure scripts
│
└── README.md
```

## Getting Started

### Prerequisites
- pnpm 8+
- Node.js 18+
- Go 1.21+ (for api-go)
- Python 3.10+ (for Python services)
- Docker (for containerization)

### Installation

```bash
pnpm install
```

### Development

Run all services in development mode:
```bash
pnpm dev
```

Or run a specific workspace:
```bash
pnpm -F @truthnet/frontend dev
```

### Building

Build all packages:
```bash
pnpm build
```

Build a specific package:
```bash
pnpm -F @truthnet/frontend build
```

### Testing

Run all tests:
```bash
pnpm test
```

## Workspace Configuration

This is a pnpm monorepo. Each directory under `apps/`, `services/`, and `packages/` is an independent workspace with its own `package.json`.

### Adding Dependencies

To add a dependency to a specific workspace:
```bash
pnpm -F @truthnet/frontend add lodash
```

To add a dev dependency:
```bash
pnpm -F @truthnet/frontend add -D typescript
```

To add a dependency across all workspaces:
```bash
pnpm add -r lodash
```

## Services

### API (Go)
Main backend service handling orchestration and business logic.

### Frontend (Next.js)
Web interface for the TruthNet platform.

### Visual Agent (Python)
Machine learning service for visual processing and analysis.

### Audio Agent
Service for audio processing and analysis.

### Lipsync Agent
Service for generating lip-sync animations.

### Metadata Agent
Service for managing metadata across the platform.

## Contributing

Please ensure all code follows the project's linting standards:
```bash
pnpm lint
```

## License

MIT
