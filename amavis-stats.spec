%include	/usr/lib/rpm/macros.perl
%define		_rc	rc6
Summary:	Simple amavisd-new statistics generator
Summary(pl):	Prosty generator statystyk dla amavisd-new
Name:		amavis-stats
Version:	0.1.13
Release:	0.%{_rc}.5
License:	GPL
Group:		Applications/System
Source0:	http://rekudos.net/download/%{name}-%{version}-%{_rc}.tar.gz
# Source0-md5:	39156ca0eba50405d836aaf9d97743bf
Source1:	%{name}.cron
Patch0:		%{name}-gzip.patch
Patch1:		%{name}-more_ac.patch
Patch2:		%{name}-Makefile.patch
URL:		http://rekudos.net/amavis-stats/
BuildRequires:	rpmbuild(macros) >= 1.268
Provides:	%{name}-%{version}-%{release}
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	/var/lib/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_webappdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
amavis-stats is a simple amavis statistics generator based on rrdtool.
It produces graphs from amavisd-new log entries of infections broken
down by virus.

%description -l pl
amavis-stats jest prostym generatorem statystyk opartym na rrdtool.
Tworzy wykresy zainfekowanych wiadomo¶ci, w rozbiciu na poszczególne
wirusy, na podstawie logów amavisd-new.

%package php
Summary:	PHP interface for amavis-stats
Summary(pl):	Interfejs PHP dla amavis-stats
Group:		Applications/System
Requires:	%{name}-%{version}-%{release}
Requires:	php
Requires:	php-pcre
Requires:	webapps

%description php
PHP interface for amavis-stats.

%description php -l pl
Interfejs PHP dla amavis-stats.

%prep
%setup -q -n %{name}-%{version}-%{_rc}
%patch0 -p1
%patch1 -p0
%patch2 -p1

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/cron.d
user=`id -u`
group=`id -g`

%{__make} install \
	install_prefix=$RPM_BUILD_ROOT \
	amavis_user=$user \
	amavis_group=$group \
	web_user=$user \
	web_group=$group

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/amavis-stats
ln -s amavis-stats.php $RPM_BUILD_ROOT%{_datadir}/%{name}/index.php
install -d $RPM_BUILD_ROOT%{_webapps}/%{_webapp}
mv $RPM_BUILD_ROOT{/etc/amavis-stats/apache.conf,%{_webapps}/%{_webapp}/httpd.conf}
cp $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/{httpd,apache}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin php -- apache1
%webapp_register apache %{_webapp}

%triggerun php -- apache1
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
%doc README debian/changelog
%attr(755,root,root) %{_sbindir}/amavis-stats
%dir %{_pkglibdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/amavis-stats
%{_mandir}/man1/*

%files php
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%dir %{_appdir}
# symlink
%{_appdir}/img
%{_appdir}/%{name}.php
%{_appdir}/index.php
%attr(775,root,http) %dir %{_pkglibdir}/img
