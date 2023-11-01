# -*- coding: utf-8 -*-
# This decides the SRPM name.  Set to "make" for a rolling release
# (like Fedora) or "make-latest" for a long term release that needs
# optional versioned updates.
Name: make-latest
Epoch: 1
Version: 4.3
Release: 1%{?dist}
License: GPLv3+
URL: http://www.gnu.org/software/make/
Source: ftp://ftp.gnu.org/gnu/make/make-%{version}.tar.gz

%if "%{name}" != "make"
# Set this to the sub-package base name, for "make-latest"
%global make make43
%if 0%{?rhel} > 0
%global _prefix /opt/rh/%{make}
%else
# We intentionally do not define a case for Fedora, as it should not
# need this functionality, and letting it error avoids accidents.
%{error:"Each downstream must specify its own /opt namespace"}
%endif
Summary: Meta package to include latest version of make
%else
%global make %{name}
Summary: A GNU tool which simplifies the build process for users
%endif

%if 0%{?rhel} > 0
# This gives the user the option of saying --with guile, but defaults to WITHOUT
%bcond_with guile
%else
# This gives the user the option of saying --without guile, but defaults to WITH
%bcond_without guile
%endif

Patch0: make-4.3-getcwd.patch

# Assume we don't have clock_gettime in configure, so that
# make is not linked against -lpthread (and thus does not
# limit stack to 2MB).
Patch1: make-4.0-noclock_gettime.patch

# BZs #142691, #17374
Patch2: make-4.3-j8k.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1827850
# https://savannah.gnu.org/bugs/?58232
# Remove on next make rebase
Patch3: make-4.3-cloexec.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=2010506
# https://savannah.gnu.org/bugs/?59093
# Remove on next make rebase
Patch4: make-4.3-filter-out.patch

# autoreconf
BuildRequires: make
BuildRequires: autoconf, automake, gettext-devel
BuildRequires: procps
BuildRequires: perl
%if %{with guile}
BuildRequires: pkgconfig(guile-2.2)
%endif
BuildRequires: gcc

%if "%{name}" != "make"
# We're still on the make-latest package
Requires: %{make}
%description -n make-latest
The latest GNU Make, with a version-specific install
%files -n make-latest

%package -n %{make}
Summary: A GNU tool which simplifies the build process for users
%endif

%description -n %{make}
A GNU tool for controlling the generation of executables and other
non-source files of a program from the program's source files. Make
allows users to build and install packages without any significant
knowledge about the details of the build process. The details about
how the program should be built are provided for make in the program's
makefile.

%package -n %{make}-devel
Summary: Header file for externally visible definitions

%description -n %{make}-devel
The %{make}-devel package contains gnumake.h.

%prep
%autosetup -n make-%{version} -p1

rm -f tests/scripts/features/parallelism.orig

%build
autoreconf -vfi

%configure \
%if %{with guile}
    --with-guile
%else
    --without-guile
%endif

%make_build

%install
%make_install
ln -sf make ${RPM_BUILD_ROOT}/%{_bindir}/gmake
ln -sf make.1 ${RPM_BUILD_ROOT}/%{_mandir}/man1/gmake.1
rm -f ${RPM_BUILD_ROOT}/%{_infodir}/dir

%if "%{name}" != "make"
install -d -m 755 ${RPM_BUILD_ROOT}/etc/scl/prefixes
dirname %{_prefix} > %{make}.prefix
install -p -m 644 %{make}.prefix ${RPM_BUILD_ROOT}/etc/scl/prefixes/%{make}

echo "export PATH=%{_prefix}/bin:\$PATH" > enable.scl
install -p -m 755 enable.scl ${RPM_BUILD_ROOT}/%{_prefix}/enable
%endif

%find_lang make

%check
echo ============TESTING===============
/usr/bin/env LANG=C make check && true
echo ============END TESTING===========

%files -n %{make} -f make.lang
%license COPYING
%doc NEWS README AUTHORS
%{_bindir}/*
%{_mandir}/man*/*
%{_infodir}/*.info*
%{_includedir}/gnumake.h
%if "%{name}" != "make"
/etc/scl/prefixes/%{make}
%{_prefix}/enable
%endif

%files -n %{make}-devel
%{_includedir}/gnumake.h

%changelog
* Thu Jul 14 2022 DJ Delorie <dj@redhat.com> - 1:4.3-1
Initial commit.
