FROM ollama/ollama:0.40.16 AS official
# Keep only CPU backend and its supporting libraries.
RUN rm -rf /usr/lib/ollama/cuda* /usr/lib/ollama/rocm* /usr/lib/ollama/vulkan* /usr/lib/ollama/mlx*
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libgomp1 libopenblas0 && rm -rf /var/lib/apt/lists/*
COPY --from=official /usr/bin/ollama /usr/bin/ollama
COPY --from=official /usr/lib/ollama /usr/lib/ollama
ENV OLLAMA_HOST=0.0.0.0:11434
EXPOSE 11434
ENTRYPOINT ["/usr/bin/ollama"]
CMD ["serve"]
