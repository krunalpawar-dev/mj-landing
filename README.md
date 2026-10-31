# MJ DYNAMIC — custom software website

A separate MJ DYNAMIC company website created from the proven portfolio codebase. It keeps the same lightweight PHP architecture, responsive static export, service and case-study catalogue, private content manager, and SQLite-backed enquiry workflow.

## What is included

- Company-led home, about, services, projects, technology, insights, contact and privacy pages.
- 12 software services and 12 project case studies, including clearly labelled concept projects.
- Reusable PHP views and content stored in `app/content.json`.
- Optional private content manager and enquiry database for PHP hosting.
- Static HTML export for GitHub Pages or any static host.
- Progressive page navigation, project filters, responsive layout and reduced-motion support.

The copied case studies and service descriptions come from the reference portfolio. Review client names, screenshots and publication permissions before using them on a new public MJ DYNAMIC domain.

## Open locally without a server

The generated site is portable plain HTML. Double-click `index.html`, or right-click it and choose a browser. Navigation, styles, images and project pages use relative file paths, so the complete site works directly from the folder.

Keep the full folder structure together. Do not move `index.html` away from `assets/`, `about/`, `services/`, `projects/` and the other generated folders.

## Run the PHP development version

Requires PHP 8.2+ with PDO SQLite, mbstring, JSON and sessions. GD and fileinfo are required for screenshot uploads.

```powershell
php -S 127.0.0.1:8086 router.php
```

Open `http://127.0.0.1:8086`. Use this mode only when developing PHP templates, the CMS or the database-backed enquiry workflow. If Herd is configured for this folder, the default application URL is `http://mj-dynamic.test`.

## Generate the static site

Set the final public origin when building. This keeps canonical URLs, the sitemap and social metadata aligned with the deployment domain.

```powershell
$env:PUBLIC_ORIGIN = 'https://your-mj-dynamic-domain.example'
python scripts/build-pages.py
python tests/test_pages.py
```

For the local default canonical origin, omit `PUBLIC_ORIGIN`.

## Validate

```powershell
npm ci
npm run test:navigation
python tests/test_site.py
python tests/test_pages.py
```

The integration tests use isolated temporary storage and never enable email delivery.

## Private configuration

Private data defaults to `../mj-dynamic-storage`, outside the repository. Keep it outside the public web root.

| Variable | Purpose |
| --- | --- |
| `APP_URL` | Canonical origin for the PHP application |
| `PUBLIC_ORIGIN` | Canonical origin used by the static build |
| `STORAGE_PATH` | Private writable storage directory |
| `CONTACT_EMAIL` | Enquiry recipient |
| `ADMIN_PASSWORD_HASH` | Administrator password hash |
| `MAIL_ENABLED` | `true` to enable PHP mail notifications |
| `MAIL_FROM` | Verified sender address |

Create the administrator password interactively:

```powershell
php scripts/create-admin.php
```

Then open `/admin`. There is no default password.

## Contact details

The new brand currently retains the contact email, phone number and LinkedIn URL from the reference portfolio in `app/config.php`. Replace those values when dedicated MJ DYNAMIC accounts are available. The static contact form continues to use the reference Formspree endpoint; confirm ownership before launch.

## Project structure

- `index.php`: routing, metadata, structured data and shared layout.
- `app/views/`, `app/partials/`: reusable server-rendered templates.
- `app/content.json`: services, projects, articles, technologies and FAQs.
- `app/admin.php`: private content and enquiry management.
- `assets/css/portfolio.css`, `assets/js/portfolio.js`: responsive design and progressive navigation.
- `scripts/build-pages.py`: static-site export.
- `tests/`: navigation, integration and generated-page validation.

## Deployment notes

Static hosting supports the generated pages and Formspree contact form only. The content manager, private database and PHP contact handler require a PHP host with HTTPS and persistent storage. Configure a real production domain before launch; no MJ DYNAMIC domain was assumed or invented in this project.
