# Build Debian package using dh-virtualenv

FROM ubuntu:groovy AS build-stage
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && apt-get install -yqq \
		dh-virtualenv devscripts dh-virtualenv dh-systemd python3.8 python3.8-venv

WORKDIR /dpkg-build
COPY ./ ./
RUN dpkg-buildpackage -us -uc -b && mkdir -p /dpkg && cp -pl /sytr[-_]* /dpkg

CMD ["ls"]
