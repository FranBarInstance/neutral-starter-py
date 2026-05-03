# Component: default_0yt2sa

Base configuration component that provides default values for the system.

## Overview

This component sets initial data that serves as base values for the system.

## How It Works

The application merges schemas from all components in load order. This component loads first (lowest prefix), so its values become the base that subsequent components can override.

## Structure

- `manifest.json` - Component identity and security settings
- `schema.json` - Default configuration values

## Usage

Other components can override these defaults by declaring the same keys in their own `schema.json`. See [Overriding Components](../../../docs/override-components.md) for details.
