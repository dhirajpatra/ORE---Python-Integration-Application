# Multi-stage build for ORE Python Application
FROM ubuntu:22.04 as ore-builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    libboost-all-dev \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Build QuantLib
WORKDIR /tmp
RUN git clone --branch QuantLib-v1.31 https://github.com/lballabio/QuantLib.git && \
    cd QuantLib && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Build ORE
WORKDIR /tmp
RUN git clone https://github.com/OpenSourceRisk/Engine.git && \
    cd Engine && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    make install

# Final stage - Python application
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libboost-filesystem1.74.0 \
    libboost-serialization1.74.0 \
    libboost-system1.74.0 \
    libboost-date-time1.74.0 \
    libboost-regex1.74.0 \
    libboost-thread1.74.0 \
    libblas3 \
    liblapack3 \
    && rm -rf /var/lib/apt/lists/*

# Copy QuantLib and ORE from builder
COPY --from=ore-builder /usr/local/lib /usr/local/lib
COPY --from=ore-builder /usr/local/bin/ore /usr/local/bin/ore
COPY --from=ore-builder /usr/local/include /usr/local/include

# Update library cache
RUN ldconfig

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY ore_app.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create directories for data
RUN mkdir -p /app/ore_input /app/ore_output /app/data

# Set Python path
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:${PATH}"

# Expose port for potential web interface (optional)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python3", "app.py"]