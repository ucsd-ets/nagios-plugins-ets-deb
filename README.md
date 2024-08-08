# Checks

## check_smartmon

```
check_smartmon --all
```

NOTE: Will fail if there's no SMART devices, e.g. on VMWare

* https://exchange.nagios.org/directory/Plugins/Operating-Systems/Linux/check_smartmon/details
* https://github.com/nihlaeth/Nagios_check_smartmon

## check_zpools

```
check_zpools -a
```

* https://exchange.nagios.org/directory/Plugins/Operating-Systems/Solaris/check_zpools-2Esh/details
* https://www.claudiokuenzler.com/nagios-plugins/check_zpools.sh

## check_mem

```
check_mem -w 90 -c 95

-w <warn %>
-c <critical %>
```

*  https://github.com/liberodark/nrpe-installer
*  https://raw.githubusercontent.com/liberodark/nrpe-installer/master/src/check_mem.c

# Compilation

```
cat << EOF > /etc/yum.repos.d/docker-rpm-builder-v1.repo
[docker-rpm-builder-v1]
name=docker-rpm-builder-v1
baseurl=https://dl.bintray.com/alanfranz/drb-v1-centos-7
repo_gpgcheck=1
gpgcheck=1
enabled=1
gpgkey=https://www.franzoni.eu/keys/D1270819.txt
       https://www.franzoni.eu/keys/D401AB61.txt
EOF
yum install docker-rpm-builder
docker-rpm-builder dir --download-sources alanfranz/docker-rpm-builder-configurations:centos-7 . /tmp/rpms
ls -l /tmp/rpms/x86_64
```

https://github.com/docker-rpm-builder/docker-rpm-builder


# How to build the deb

1. Install debuild

       sudo apt-get install -y \
              dpkg-dev \
              devscripts \
              build-essential \
              lintian \
              debhelper

2. Clone the debian package repo

        git clone https://github.com/ucsd-ets/nagios-plugins-ets-deb.git

3. Download the source tarball

        wget -O ../nagios-plugins-ets_1.4.orig.tar.gz https://github.com/ucsd-ets/nagios-plugins-ets/archive/refs/tags/1.2.tar.gz

4. Extract source

        tar zxvf ../nagios-plugins-ets_1.4.orig.tar.gz --strip-components=1

5. Run debuild

        debuild -us -uc

6. Check the output
        dpkg -c ../nagios-plugins-ets_1.4_amd64.deb

See:
* https://blog.packagecloud.io/buildling-debian-packages-with-debuild/
* https://metebalci.com/blog/a-minimum-complete-example-of-debian-packaging-and-launchpad-ppa-hellodeb/
* https://www.debian.org/doc/manuals/debmake-doc/ch04.en.html

# Installation

    dpkg -i nagios-plugins-ets-1.4.deb



# notes

debuild calls dh build which calls dh_auto_build which calls make -j1 which selects the 1st goal which is install.

When I've added

all:
before install to makefile, the problem was solved.
