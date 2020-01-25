#
# TODO:
#   - add trigger to update apache configuration when upgrading from
#     older versions (not sure if this is required)
#
Summary:	Simple amavisd-new statistics generator
Summary(pl.UTF-8):	Prosty generator statystyk dla amavisd-new
Name:		amavis-stats
Version:	0.1.22
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://downloads.topicdesk.com/amavis_stats/%{name}-%{version}.tar.gz
# Source0-md5:	5bea6811c00a4fda4b96b6a318a04a92
Source1:	%{name}.init
Patch0:		%{name}-gzip.patch
Patch1:		%{name}-Makefile.patch
Patch2:		%{name}-pid.patch
URL:		http://osx.topicdesk.com/content/view/42/59/
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
Provides:	%{name}-%{version}-%{release}
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	/var/lib/%{name}
%define		_pkgcachedir	/var/cache/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_webappdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
amavis-stats is a simple amavis statistics generator based on rrdtool.
It produces graphs from amavisd-new log entries of infections broken
down by virus.

%description -l pl.UTF-8
amavis-stats jest prostym generatorem statystyk opartym na rrdtool.
Tworzy wykresy zainfekowanych wiadomości, w rozbiciu na poszczególne
wirusy, na podstawie logów amavisd-new.

%package php
Summary:	PHP interface for amavis-stats
Summary(pl.UTF-8):	Interfejs PHP dla amavis-stats
Group:		Applications/System
Requires:	%{name}-%{version}-%{release}
Requires:	php(pcre)
Requires:	webapps
Requires:	webserver(php)

%description php
PHP interface for amavis-stats.

%description php -l pl.UTF-8
Interfejs PHP dla amavis-stats.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
sed -i -e '/basic_machine=powerpc-apple/s/$/\n\t\t;;\n\tnoarch-*)\n\t\tbasic_machine=noarch/;' config.sub
%configure \
	--with-user=root \
	--with-group=http \
	--with-log-file=/var/log/maillog
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_webapps}/%{_webapp}}
mv $RPM_BUILD_ROOT{%{_datadir}/amavis-stats/amavis-stats.alias.conf,%{_webapps}/%{_webapp}/httpd.conf}
mv $RPM_BUILD_ROOT{%{_datadir}/amavis-stats/amavis-stats.php.conf,%{_webapps}/%{_webapp}}
ln -s %{_webapps}/%{_webapp}/amavis-stats.php.conf $RPM_BUILD_ROOT%{_datadir}/%{name}/amavis-stats.php.conf
cp $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/{httpd,apache}.conf
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/amavis-stats

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin php -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun php -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin php -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun php -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun php -- %{name}-php < 0.1.13-0.rc6.4.1
if [ -f /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}\/apache.conf/d" /etc/httpd/httpd.conf
fi

if [ -f /etc/%{name}/apache.conf.rpmsave ]; then
	cp -f %{_webapps}/%{_webapp}/httpd.conf{,.rpmnew}
	mv -f /etc/%{name}/apache.conf.rpmsave %{_webapps}/%{_webapp}/httpd.conf
fi

rm -f /etc/httpd/httpd.conf/99_%{name}.conf
/usr/sbin/webapp register httpd %{_webapp}
%service -q httpd reload

%files
%defattr(644,root,root,755)
%doc README ChangeLog
%attr(754,root,root) /etc/rc.d/init.d/amavis-stats
%attr(755,root,root) %{_sbindir}/amavis-stats
%dir %{_pkglibdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/amavis-stats.conf
%{_mandir}/man1/*

%files php
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/amavis-stats.php.conf
%dir %{_appdir}
%{_appdir}/amavis-stats.php.conf
%{_appdir}/img
%{_appdir}/includes
%{_appdir}/index.php
%{_appdir}/templates
%{_appdir}/%{name}.php
%{_appdir}/%{name}.html
%{_appdir}/*.png
%{_appdir}/*.ttf
%attr(775,root,http) %dir %{_pkgcachedir}
