FROM golang:1.23-alpine AS gitleaks-build
RUN apk add --no-cache bash git openssh-client
WORKDIR /app
RUN git clone https://github.com/gitleaks/gitleaks.git && \
	cd gitleaks && \
	VERSION=$(git describe --tags --abbrev=0) && \
	CGO_ENABLED=0 go build -o bin/gitleaks -ldflags "-X=github.com/zricethezav/gitleaks/v8/cmd.Version=${VERSION}"

FROM golang:bullseye AS trufflehog-builder

RUN apt update && apt install git

WORKDIR /build

RUN git clone https://github.com/trufflesecurity/trufflehog.git

ENV CGO_ENABLED=0
ARG TARGETOS TARGETARCH
WORKDIR /build/trufflehog
RUN --mount=type=cache,target=/go/pkg/mod \
	--mount=type=cache,target=/root/.cache/go-build \
	GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -o trufflehog .

FROM python:3.11-alpine
RUN apk add --no-cache bash git openssh-client
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=gitleaks-build /app/gitleaks/bin/* /usr/bin/

COPY --from=trufflehog-builder /build/trufflehog/trufflehog /usr/bin/trufflehog

RUN git config --global --add safe.directory '*'

WORKDIR /sec-m8

CMD ["python", "/app/main.py"]