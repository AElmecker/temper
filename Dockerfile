FROM ubuntu:22.04
LABEL maintainer "tuan t. pham" <tuan@vt.edu>

ENV PKGS="python3 python3-serial python3-pip" \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get -yq update && apt-get dist-upgrade -yq \
    && apt-get -yq install --no-install-recommends  ${PKGS} \
    && pip3 install prometheus-client \
    && pip3 install pyyaml

RUN apt-get autoremove -yq \
    && apt-get autoclean \
    && rm -fr /tmp/* /var/lib/apt/lists/*

RUN mkdir -p /opt/temper/bin

COPY temper.py /opt/temper/bin
COPY prometheus_exporter_config.py /opt/temper/bin
COPY temper-prometheus-exporter.py /opt/temper/bin

EXPOSE 2610

WORKDIR /opt/temper/bin
# This is used at commandline such as
# docker run --rm -it temper/service:latest -h
ENTRYPOINT  ["/opt/temper/bin/temper-prometheus-exporter.py", "--config=/etc/config.yml"]
