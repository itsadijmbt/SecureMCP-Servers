# Dispatch Local UI

React-based development environment for the CLI's Local UI.

## Overview

The CLI serves a simple, static Local UI (HTML/CSS/JS) for managing agents locally. This system lets us develop using modern React components and tooling, then compile everything into static assets that the CLI can serve.

**Why this approach:**
- Develop with React's ecosystem and reuse components from web-app
- Maintain CLI's simplicity (just serves static files)
- Share design system between web-app and CLI interfaces

## Quick Start

```bash
cd cli/dispatch-local-ui
npm install --min-release-age=30
npm run dev              # Development server at http://localhost:3001
```

For CLI testing:
```bash
npm run deploy-update   # Build + reinstall CLI
dispatch router start   # Start router in background
```

## Development

### Components
- **React components** in `src/components/`
- **Import shared UI** from web-app: `import { Button } from '@ui/button'`
- **Available components**: Button, Card, Badge, Input, Textarea

### Workflow
1. **Develop** - `npm run dev`
2. **Deploy** - `npm run deploy-update`
3. **Test** - `dispatch router start`
4. **Logs** - `dispatch router logs --follow`

## Architecture

```
cli/dispatch-local-ui/src/
├── components/          # Local UI components (React)
├── index.js            # Application entry point
└── styles.css          # Tailwind + design system

→ npm run deploy-update → cli/dispatch_cli/router/static/
                        ├── index.html
                        ├── components.js
                        └── components.css
```

The build process compiles React components to static assets served by the CLI.

## Commands

```bash
npm run dev              # Development server
npm run deploy-update    # Build + reinstall CLI (recommended)
npm run build           # Build static assets only
npm run sync-components # Sync shared components from web-app
```

## Build Configuration

- **Webpack** (`pack/webpack.config.js`) - Compiles React → vanilla JS
- **@ui alias** - Points to `../../web-app/src/components/ui/` for component imports
- **Output** - Static files in `cli/dispatch_cli/router/static/`
- **Tailwind** - Processes design system CSS with shared tokens
