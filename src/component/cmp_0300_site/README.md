# Component: site_0yt2sa

Site data and translations provider.

## Overview

This component provides project-specific site branding data and translations. It overrides default values from `default_0yt2sa` with the actual application branding.

## Structure

- `manifest.json` - Component identity
- `schema.json` - Site data, translations, and menu placeholders

## Site Data Provided

| Key | Purpose |
|-----|---------|
| `name` | Site name |
| `title` | Page title |
| `description` | SEO description |
| `cover` | Cover image path |
| `logo` | Logo image path |
| `static` | Static assets path |
| `home_link` | Home page link |

## Translations

Covers 6 languages: EN, ES, DE, FR, AR, ZH

## Menu Placeholders

Reserves navbar language menu positions for anonymous and authenticated users.

## Usage

Templates access site data via:

```ntpl
{:;current->site->name:}
{:;current->site->title:}
{:trans; Neutral TS ! :}
```
