# Public repository setup

Repository: `homegundredaroad/Vaping26`

Public site: `https://homegundredaroad.github.io/Vaping26/`

## GitHub Pages

The repository uses a custom GitHub Actions deployment rather than the generic Static HTML/Jekyll starter workflow.

In **Settings → Pages**, set **Build and deployment → Source** to **GitHub Actions**. No other Pages source configuration is required.

`.github/workflows/validate-public.yml` then performs the publication sequence automatically on `main`:

1. validate the disclosure boundary and publication manifest;
2. run public-site regression tests;
3. build the static publication bundle with `scripts/build_site.py`;
4. upload `build/site/` as the Pages artifact;
5. deploy only after the validation/build job succeeds.

No external API keys or repository secrets are required for GitHub Pages publication.

## Public build contract

`site/` contains maintained website code. The builder adds only these generated public roots to the deployment artifact:

- `data/public/`
- `evidence/`
- `provenance/`

Private/raw Research trees are not copied into the Pages artifact. `build/` is generated locally or in Actions and remains gitignored.

## Research publication source

Approved generated research outputs arrive from the private `Vaping26-Research` repository through its deny-by-default publication firewall. A successful Research publication pushes only allowlisted generated outputs into this repository. That push then triggers the public validation/build/Pages workflow automatically.

The public repository must not pull raw research data from the private repository.

## Optional Hostinger deployment

Hostinger remains a manual optional deployment target. The Hostinger workflow now builds the same validated `build/site/` bundle used by GitHub Pages so the two public surfaces cannot drift merely because different source directories were deployed.

### Repository Secrets for Hostinger

- `HOSTINGER_HOST` — SSH/SFTP hostname or IP from hPanel.
- `HOSTINGER_USERNAME` — SSH/SFTP username.
- `HOSTINGER_SSH_PRIVATE_KEY` — private half of a dedicated deploy key. Never commit it.
- `HOSTINGER_PASSWORD` — optional password fallback if a deploy key is not used.

The existing SCC Webdesign test-hosting fallback secret names remain supported by the workflow.

### Repository Variables for Hostinger

- `HOSTINGER_PORT` — SSH port shown in hPanel.
- `HOSTINGER_TARGET_DIR` — absolute deployment directory. As a safety guard, the configured path must contain `vaping26`.

The matching public SSH key must be added to Hostinger before key-based deployment.
