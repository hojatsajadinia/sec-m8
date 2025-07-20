FROM golang:1.23-alpine:sha256:ddcd26ec6b109c838725a1d93e3bec6d8b9c47f1fdc696b58820c63c70349c9a AS gitleaks-build

WORKDIR /app
RUN git clone https://github.com/gitleaks/gitleaks.git && \
	cd gitleaks && \
	VERSION=$(git describe --tags --abbrev=0) && \
	CGO_ENABLED=0 go build -o bin/gitleaks -ldflags "-X=github.com/zricethezav/gitleaks/v8/cmd.Version=${VERSION}"


FROM python:3.11-alpine:sha256:9ce54d7ed458f71129c977478dd106cf6165a49b73fa38c217cc54de8f3e2bd0
RUN apk add --no-cache bash git openssh-client

COPY --from=gitleaks-build /app/gitleaks/bin/* /usr/bin/
RUN git config --global --add safe.directory '*'
