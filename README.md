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
