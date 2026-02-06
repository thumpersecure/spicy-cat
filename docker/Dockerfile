# ══════════════════════════════════════════════════════════════════════════
#  spicy-cat Docker Privacy Container
#
#     /\_____/\
#    /  o   o  \
#   ( ==  ^  == )  "Containerized anonymity."
#    )         (
#   (           )
#  ( (  )   (  ) )
# (__(__)___(__)__)
#
#  Advanced fingerprint protection + telemetry confusion in a container.
#
#  Build:  docker build -t spicy-cat .
#  Run:    docker-compose up
#
# ══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim-bookworm AS base

LABEL maintainer="spicy-cat project"
LABEL description="Privacy-first container with advanced fingerprint protection and telemetry confusion"
LABEL version="1.1.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ── System Dependencies ──────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Network tools for TCP/IP stack normalization
    iptables \
    iproute2 \
    iputils-ping \
    net-tools \
    # DNS tools
    dnsutils \
    dnsmasq \
    # TLS/SSL tools
    openssl \
    ca-certificates \
    # WiFi tools (for telemetry confusion)
    wireless-tools \
    # System utilities
    procps \
    curl \
    wget \
    # Timezone data
    tzdata \
    # Firefox ESR for browser fingerprint protection
    firefox-esr \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ── Python Dependencies ──────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    faker \
    cryptography \
    scapy \
    requests

# ── Create Application Directory ─────────────────────────────────────────
WORKDIR /opt/spicy-cat

# ── Copy Application Code ────────────────────────────────────────────────
COPY lib/ ./lib/
COPY wifi/ ./wifi/
COPY spicy-cat.py ./
COPY spicy-cat.sh ./
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/healthcheck.sh /healthcheck.sh

# ── Set Permissions ──────────────────────────────────────────────────────
RUN chmod +x /entrypoint.sh /healthcheck.sh spicy-cat.py spicy-cat.sh \
    && chmod +x wifi/spicy-wifi.py

# ── Create Runtime Directories ───────────────────────────────────────────
RUN mkdir -p /root/.spicy-cat/identities \
    /root/.spicy-cat/browsers \
    /var/log/spicy-cat \
    /tmp/spicy-cat

# ── Default Environment Variables ────────────────────────────────────────
# These can be overridden at runtime via docker-compose or docker run
ENV SPICY_CAT_MODE="full" \
    SPICY_CAT_AGENT="true" \
    SPICY_CAT_TELEMETRY_CHAOS="true" \
    SPICY_CAT_FINGERPRINT="true" \
    SPICY_CAT_DNS_CHAFF="true" \
    SPICY_CAT_PHANTOM_SWARM="true" \
    SPICY_CAT_LOG_LEVEL="INFO" \
    SPICY_CAT_ROTATION_INTERVAL="1800" \
    SPICY_CAT_THREAT_RESPONSE="auto" \
    PYTHONUNBUFFERED=1

# ── Health Check ─────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD /healthcheck.sh

# ── Expose No Ports (privacy first) ─────────────────────────────────────
# No ports exposed by default - all traffic goes outbound through
# the container's network stack with fingerprint protection applied.

# ── Entrypoint ───────────────────────────────────────────────────────────
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "spicy-cat.py", "dashboard"]
