from ubuntu:14.04.2
maintainer guido.stevens@cosent.net
run apt-get update
run apt-get update && apt-get install -y python-dev gcc make zlib1g-dev libjpeg-dev python-virtualenv git-core libfreetype6-dev gettext python-pip libxslt1-dev python-lxml jed firefox xvfb npm nodejs ruby ruby-dev libenchant-dev python-gdbm python-tk graphicsmagick poppler-utils poppler-data ghostscript pdftk libreoffice chromium-browser chromium-chromedriver
run ln -s /usr/bin/nodejs /usr/local/bin/node
run gem install bundler
run gem install docsplit
run locale-gen en_US.UTF-8 nl_NL@euro
run useradd -m -d /app app && echo "app:app" | chpasswd && adduser app sudo
run mkdir /.npm && chown app.app /.npm
run mkdir /.config && chown app.app /.config
run mkdir /.cache && chown app.app /.cache
run mkdir /.local && chown app.app /.local
run echo ploneintranet > /etc/debian_chroot
cmd ["/bin/bash"]
