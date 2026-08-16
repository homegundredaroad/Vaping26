# Public repository setup

Repository: `homegundredaroad/Vaping26`

Public site: `https://homegundredaroad.github.io/Vaping26/`

## GitHub Pages

In **Settings → Pages**, use **Build and deployment → Source → GitHub Actions**.

`.github/workflows/validate-public.yml` performs:

1. public disclosure/manifest validation;
2. public-site regression tests;
3. static build with `scripts/build_site.py`;
4. upload of `build/site/` as the Pages artifact;
5. Pages deployment only after validation/build succeeds.

No external API keys are required for GitHub Pages publication.

## Public build contract

`site/` contains maintained website code. The builder can stage only these generated public roots:

- `data/public/`
- `evidence/`
- `environment/` (legacy optional background-context registry)
- `regulation/`
- `provenance/`

Raw/private Research trees are never copied into the Pages artifact.

## Research publication source

Approved outputs arrive from private `Vaping26-Research` through its deny-by-default publication firewall. Automatic publication is restricted to successful `main` harvests; a manual workflow can publish a specifically selected successful harvest run.

The V3 publisher preserves static repository README/documentation files while replacing generated JSON outputs.

## Optional environmental context

The normal V3 Research harvest is vaping-first. Ambient/satellite collectors are opt-in and are not required to publish the Observatory.

## Optional Hostinger deployment

Hostinger remains a manual optional target and builds the same validated `build/site/` bundle used by Pages. Keep host credentials in repository secrets and configure a target directory containing `vaping26` as required by the workflow safety guard.
