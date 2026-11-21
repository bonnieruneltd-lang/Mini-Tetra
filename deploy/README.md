# Deploy templates

These are **templates**, not a turnkey installer. They encode the decisions from
the study: one Forge API per GPU, models read-only over NFS, outputs per worker,
systemd/Docker restart policy, a queue behind Caddy, and a UPS shutdown path.

The compose file assumes your Forge image honours two environment variables:
`PORT` (API port) and `COMMANDLINE_ARGS` (Forge/A1111 flags). Most community
Forge images do; if yours does not, change the service `command:` instead of
`COMMANDLINE_ARGS`. Pin the image by digest in production.

## 1. Worker host

```bash
sudo apt update && sudo apt install -y nfs-common curl
sudo ubuntu-drivers install   # then reboot; verify the pinned branch with nvidia-smi
# Docker Engine + NVIDIA Container Toolkit per the official docs, then:
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
nvidia-smi
```

Mount the model share (replace the head IP):

```
10.20.0.10:/srv/models /srv/models nfs4 ro,vers=4.2,rsize=1M,wsize=1M,hard,timeo=600,retrans=2,_netdev,nofail 0 0
```

```bash
sudo mkdir -p /srv/models /srv/outputs /srv/forge
sudo mount -a && findmnt /srv/models
sudo mkdir -p /srv/outputs/$(hostname)
```

## 2. Start the worker

```bash
sudo cp compose.worker.yml /srv/forge/compose.yml
cd /srv/forge
echo 'FORGE_IMAGE=forge-worker:2026.11' | sudo tee .env
sudo docker compose config      # validates interpolation and GPU syntax
sudo docker compose up -d
sudo docker compose ps
curl -fsS http://127.0.0.1:7860/sdapi/v1/options >/dev/null && echo API-OK
```

On a dual-GPU node, uncomment `forge-1` (port 7861, `device_ids: ["1"]`).

## 3. Register with the queue

In SwarmUI on the head, add each backend as `http://<worker-host>:7860`
(and `:7861` on dual-GPU nodes). Keep the worker API ports firewalled to the head
and the management VLAN; users should only reach Caddy.

## 4. Caddy on the head

```bash
sudo apt install -y caddy
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Set `FORGE_DOMAIN` and `ACME_EMAIL` in `/etc/caddy/environment` (or the systemd
unit), then generate the password hash with `caddy hash-password`. Port 7801 is
SwarmUI's default; change `reverse_proxy` if you moved it.

## 5. UPS shutdown (NUT on the head)

```ini
# /etc/nut/ups.conf
[ups]
	driver = usbhid-ups
	port = auto
```

```ini
# /etc/nut/upsd.users
[monuser]
	password = secret
	upsmon primary
```

```ini
# /etc/nut/upsmon.conf
MONITOR ups@localhost 1 monuser secret primary
MINSUPPLIES 1
SHUTDOWNCMD "/sbin/shutdown -h +0"
POLLFREQ 5
POLLFREQALERT 5
HOSTSYNC 15
DEADTIME 15
POWERDOWNFLAG /etc/killpower
```

Start `nut-driver`, `nut-server` and `nut-monitor`. Test with `upsc ups` and by
pulling the input plug for 30 seconds. Workers should be shut down first; a
one-line SSH loop from the head's `NOTIFYCMD` is enough for a small cluster.

## 6. Smoke test

```bash
curl -fsS http://127.0.0.1:7860/sdapi/v1/txt2img \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"a red cube on a table","steps":8,"width":512,"height":512}' \
  | head -c 200
```

Then run the 48-hour soak, thermal soak and failure drills in
`../reports/cluster-design.md`.

## Notes

- `network_mode: host` keeps NFS and the API simple; do not also publish ports.
- `ipc: host` avoids shared-memory limits with PyTorch dataloaders.
- The healthcheck hits `/sdapi/v1/options`; it returns 200 only when the API is up.
  It needs `curl` in the image; swap it for `wget -q -O-` if your image lacks curl.
- A `start_period` of 300 s covers a cold model load; tune it to your largest checkpoint.
- Never hot-plug an OCuLink cable. Power the dock and host down first.
- Keep the compose file and `.env` in git; keep secrets out of it.
