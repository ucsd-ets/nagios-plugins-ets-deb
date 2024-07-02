Name:           nagios-plugins-ets
Version:        1.4
Release:        1%{?dist}
Summary:        test

License:        test
URL:            test
%undefine _disable_source_fetch
%global _python_bytecompile_extra 0
%undefine __brp_python_bytecompile
#Source0:        https://github.com/liberodark/nrpe-installer/archive/0.8.0-1.tar.gz
Source0:        https://raw.githubusercontent.com/liberodark/nrpe-installer/master/src/check_mem.c
Source1:        https://raw.githubusercontent.com/nihlaeth/Nagios_check_smartmon/master/check_smartmon.py
Source2:        http://www.claudiokuenzler.com/nagios-plugins/check_zpools.sh
Source3:        https://raw.githubusercontent.com/duffycop/nagios_plugins/master/plugins/check_service
Source4:        https://raw.githubusercontent.com/ucsd-ets/nagios-plugins-ets/master/check_smartmon2.py
Source5:        https://raw.githubusercontent.com/ucsd-ets/nagios-plugins-ets/master/check_smartctl
# https://github.com/liberodark/nrpe-installer
#BuildRequires:  
Requires:       python-psutil, smartmontools

%description


%prep
env | grep BUILD
env | grep SOURCE

# %%setup -n nrpe-installer-0.8.0-1

%build
#wget https://raw.githubusercontent.com/liberodark/nrpe-installer/master/src/check_mem.c
gcc $RPM_SOURCE_DIR/check_mem.c -o $RPM_BUILD_DIR/check_mem
echo xyz
# %%configure
#make %{?_smp_mflags}


%install

ls -al $RPM_SOURCE_DIR
ls -al $RPM_BUILD_DIR
rm -rf $RPM_BUILD_ROOT
#make install DESTDIR=%{buildroot}
install -d -m 0755 $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/
install -m 0755 $RPM_BUILD_DIR/check_mem $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_mem
install -m 0755 $RPM_SOURCE_DIR/check_smartmon.py $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_smartmon.py
install -m 0755 $RPM_SOURCE_DIR/check_smartmon2.py $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_smartmon2.py
install -m 0755 $RPM_SOURCE_DIR/check_zpools.sh $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_zpools.sh
install -m 0755 $RPM_SOURCE_DIR/check_service $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_service
install -m 0755 $RPM_SOURCE_DIR/check_smartctl $RPM_BUILD_ROOT/usr/lib64/nagios/plugins/check_smartctl
# %%make_install
ls -al $RPM_BUILD_ROOT/usr/lib64/nagios/plugins


%files
#%exclude /usr/lib64/nagios/plugins/*.pyc
#%exclude /usr/lib64/nagios/plugins/*.pyo
/usr/lib64/nagios/plugins/*.pyc
/usr/lib64/nagios/plugins/*.pyo
/usr/lib64/nagios/plugins/check_mem
/usr/lib64/nagios/plugins/check_smartmon.py
/usr/lib64/nagios/plugins/check_smartmon2.py
/usr/lib64/nagios/plugins/check_zpools.sh
/usr/lib64/nagios/plugins/check_service
/usr/lib64/nagios/plugins/check_smartctl


#%doc



%changelog

# %%clean
#rm -rf $RPM_BUILD_ROOT
