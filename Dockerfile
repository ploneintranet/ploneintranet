FROM quaive/ploneintranet-base:latest
MAINTAINER guido.stevens@cosent.net
RUN apt-get update && apt-get install -y \
    ldap-utils \
    ldapvi \
    nodejs \
    npm \
    slapd
RUN ln -s /usr/bin/nodejs /usr/local/bin/node
RUN gem install bundler
RUN useradd -m -d /app app && echo "app:app" | chpasswd && adduser app sudo
RUN mkdir /.npm && chown app.app /.npm
RUN mkdir /.config && chown app.app /.config
RUN mkdir /.cache && chown app.app /.cache
RUN mkdir /.local && chown app.app /.local
RUN echo ploneintranet > /etc/debian_chroot
CMD ["/bin/bash"]
