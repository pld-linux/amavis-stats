%include	/usr/lib/rpm/macros.perl
Summary:	Simple amavisd-new statistics generator
Summary(pl):	Prosty generator statystyk dla amavisd-new
Name:		amavis-stats
Version:	0.1.10
Release:	3
License:	GPL
Group:		Applications/System
# http://rekudos.net/download/amavis-stats.tar.gz
Source0:	ftp://distfiles.pld-linux.org/src/%{name}-%{version}.tar.gz
# Source0-md5:	12288bbf8cf9da0fec64c9660712892a
Source1:	%{name}.cron
Patch0:		%{name}-gzip.patch
URL:		http://rekudos.net/amavis-stats/
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}
%define		_htmldir		/home/services/httpd/html

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

%description php
PHP interface for amavis-stats.

%description php -l pl
Interfejs PHP dla amavis-stats.

%prep
%setup -q
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/{cron.d,httpd},%{_bindir},%{_mandir}/man1} \
	$RPM_BUILD_ROOT{%{_pkglibdir},%{_htmldir}/%{name}/img}

install amavis-stats $RPM_BUILD_ROOT%{_bindir}
install amavis-stats.php $RPM_BUILD_ROOT%{_htmldir}/%{name}/index.php
install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/amavis-stats
install amavis-stats.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/amavis-stats
%dir %{_pkglibdir}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/cron.d/amavis-stats
%{_mandir}/man1/*

%files php
%defattr(644,root,root,755)
%dir %{_htmldir}/%{name}
%dir %attr(755,http,root) %{_htmldir}/%{name}/img
%{_htmldir}/%{name}/index.php
