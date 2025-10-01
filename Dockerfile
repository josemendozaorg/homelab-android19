FROM debian:bookworm-slim

# Install system dependencies including Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    openssh-client \
    git \
    curl \
    wget \
    vim \
    make \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install HashiCorp tools (Terraform and Packer)
RUN wget -O- https://apt.releases.hashicorp.com/gpg | \
    gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" | \
    tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform packer && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment and install Python dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir \
    ansible \
    ansible-lint \
    yamllint \
    molecule \
    molecule-docker \
    pytest \
    pytest-xdist

# Create workspace directory
WORKDIR /workspace

# Set up SSH directory
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Create entrypoint script to handle SSH setup
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -d "/tmp/.ssh" ]; then' >> /entrypoint.sh && \
    echo '    cp -r /tmp/.ssh/* /root/.ssh/ 2>/dev/null || true' >> /entrypoint.sh && \
    echo '    chmod 700 /root/.ssh' >> /entrypoint.sh && \
    echo '    chmod 600 /root/.ssh/* 2>/dev/null || true' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["tail", "-f", "/dev/null"]