%include	/usr/lib/rpm/macros.perl
%define		_rc	rc6
Summary:	Simple amavisd-new statistics generator
Summary(pl):	Prosty generator statystyk dla amavisd-new
Name:		amavis-stats
Version:	0.1.13
Release:	0.%{_rc}.2
License:	GPL
Group:		Applications/System
Source0:	http://rekudos.net/download/%{name}-%{version}-%{_rc}.tar.gz
# Source0-md5:	39156ca0eba50405d836aaf9d97743bf
Source1:	%{name}.cron
Patch0:		%{name}-gzip.patch
Patch1:		%{name}-more_ac.patch
URL:		http://rekudos.net/amavis-stats/
BuildArch:	noarch
Provides:	%{name}-%{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}
%define		_phpdir			/usr/share/%{name}

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
Requires:	php-pcre

%description php
PHP interface for amavis-stats.

%description php -l pl
Interfejs PHP dla amavis-stats.

%prep
%setup -q -n %{name}-%{version}-%{_rc}
%patch0 -p1
%patch1 -p0

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

cd $RPM_BUILD_ROOT%{_datadir}/%{name}/
ln -s amavis-stats.php index.php


%clean
rm -rf $RPM_BUILD_ROOT

%post php
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*/etc/%{name}/apache.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/%{name}/apache.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/usr/sbin/apachectl restart 1>&2
fi

%preun php
if [ "$1" = "0" ]; then
	umask 027
	grep -v "^Include.*/etc/%{name}/apache.conf" /etc/httpd/httpd.conf > \
		etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/usr/sbin/apachectl restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README debian/changelog
%attr(755,root,root) %{_sbindir}/amavis-stats
%dir %{_pkglibdir}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/cron.d/amavis-stats
%{_mandir}/man1/*

%files php
%defattr(644,root,root,755)
%dir /etc/%{name}
%attr(640,root,root) %config(noreplace) /etc/%{name}/apache.conf
%dir %{_phpdir}
%dir %attr(755,http,root) %{_phpdir}/img
%{_phpdir}/%{name}.php
%{_phpdir}/index.php
%attr(755,http,http) %dir %{_pkglibdir}/img
