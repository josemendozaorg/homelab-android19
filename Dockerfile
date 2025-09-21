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
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install Python dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir \
    ansible \
    ansible-lint \
    yamllint \
    molecule \
    molecule-docker

# Create workspace directory
WORKDIR /workspace

# Copy project files
COPY . /workspace/

# Set up SSH directory
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Default command
CMD ["bash"]