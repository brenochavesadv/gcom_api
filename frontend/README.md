# Flutter frontend

This directory is the Flutter side of the monorepo. Add applications under `apps/` and reusable Dart packages under `packages/`.

Recommended layout:

```text
frontend/
├── apps/
│   └── gcom_app/
├── packages/
│   └── api_client/
└── melos.yaml
```

The existing Flutter workspace at `D:/GitHub/Flutter/flutter-monorepo` can be migrated into this directory when the target app and package ownership are confirmed. No Flutter sources were copied automatically because that would duplicate an independent workspace and its generated files.
