# CLAUDE.md

## Repository-specific instructions

- Keep changes minimal and lean.
- If a task depends on OT-2 access and SSH is not working, stop and report back instead of committing speculative changes.
- On the OT-2, prefer `curl` + `pip`; do not assume `git`, GitHub CLI, or even `bash` are available.

## SSH into an OT-2 over Tailscale

1. Make sure the runner is on the tailnet first. This repo already wires that up in `.github/workflows/copilot-setup-steps.yml` with `tailscale/github-action@v2`.
2. Prefer the `OT2_SIMULATOR_SSH` secret/environment variable when it is available. Its format is `<user>@<hostname>`.
3. Connect from a terminal, not Playwright:

   ```bash
   ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no "$OT2_SIMULATOR_SSH"
   ```

   If needed, connect directly to a Tailscale hostname such as `root@ot2-simulator-<id>.tail6a1dd7.ts.net`.
4. If the SSH flow prints a Tailscale login URL, send that URL to the user and wait for them to complete the auth step.
5. If access still fails, ask the user to verify the Tailscale tag, ACLs, and Copilot firewall allowlist before continuing.

## OT-2 shell quirks

- The device shell is `ash`, not `bash`.
- Command history lives in `/root/.ash_history`.
- Non-interactive SSH sessions may not load the Prefect environment automatically; source `/root/.profile` before running `prefect` or Python commands.
- Do not hardcode hostnames, API keys, or other secrets. Use environment variables such as `OT2_HOSTNAME` and `PREFECT_API_KEY`, and never print secret values.
