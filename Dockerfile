FROM golang:1.23-alpine AS gitleaks-build
RUN apk add --no-cache bash git openssh-client
WORKDIR /app
RUN git clone https://github.com/gitleaks/gitleaks.git && \
	cd gitleaks && \
	VERSION=$(git describe --tags --abbrev=0) && \
	CGO_ENABLED=0 go build -o bin/gitleaks -ldflags "-X=github.com/zricethezav/gitleaks/v8/cmd.Version=${VERSION}"


FROM python:3.11-alpine

RUN apk add --no-cache bash git openssh-client

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=gitleaks-build /app/gitleaks/bin/* /usr/bin/

RUN git config --global --add safe.directory '*'

WORKDIR /sec-m8

CMD ["python", "/app/main.py"]