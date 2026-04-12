FROM debian:bookworm-slim

ARG STEAMPIPE_VERSION=2.4.1
ARG TARGETARCH

LABEL maintainer="amartingarcia, ialejandro"
LABEL org.opencontainers.image.title="Steampipe"
LABEL org.opencontainers.image.description="Steampipe CLI — Use SQL to query cloud APIs"
LABEL org.opencontainers.image.source="https://github.com/devops-ia/steampipe"
LABEL org.opencontainers.image.vendor="devops-ia"
LABEL org.opencontainers.image.url="https://steampipe.io"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl jq && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://github.com/turbot/steampipe/releases/download/v${STEAMPIPE_VERSION}/steampipe_linux_${TARGETARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/steampipe

# UID 9193, GID 0 (OpenShift compatible)
RUN useradd -u 9193 -g 0 -d /home/steampipe -m -s /bin/bash steampipe

RUN mkdir -p /home/steampipe/.steampipe/{config,internal,logs,plugins} \
             /workspace && \
    chown -R 9193:0 /home/steampipe /workspace && \
    chmod -R g=u /home/steampipe /workspace

ENV STEAMPIPE_UPDATE_CHECK=false \
    STEAMPIPE_TELEMETRY=none \
    STEAMPIPE_INSTALL_DIR=/home/steampipe/.steampipe \
    STEAMPIPE_LOG_LEVEL=warn

USER 9193
WORKDIR /home/steampipe

EXPOSE 9193

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD bash -c 'echo > /dev/tcp/localhost/9193' || exit 1

CMD ["steampipe", "service", "start", "--foreground"]
