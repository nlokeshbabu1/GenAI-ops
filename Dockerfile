#We are importing the python as base image

FROM python:3.9-slim as base

# Set the working directory in the container
WORKDIR /app

#Copy the requirements file into the container
COPY requirements.txt .

#Install the dependencies
RUN mkdir -p /app/depds &&\
    pip install --no-cache-dir --target /app/depds -r requirements.txt

###########
# Development stage
###########
# FROM base as development

# # Install additional tools for development
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     git \
#     vim \
#     && rm -rf /var/lib/apt/lists/*

#############
# PProduction stage
#############
FROM base as production

#create the not root user to run the application and test premissions
# Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

#copy the dependencies from the base image
COPY --from=base /app/depds /app/depds

#install the dependencies in the production image
RUN pip install --no-cache-dir /app/depds/*

# Copy the application code into the container
COPY aiops_openserach.py .
COPY prometheus.py .
COPY AiOps.py .
COPY app.py .

#chnage the ownership of the application files to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

#health
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]