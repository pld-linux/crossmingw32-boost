#
# Conditional build:
%bcond_with	serialization	# enable Boost Serialization
#
%define		realname	boost
Summary:	The Boost C++ Libraries - MinGW32 cross version
Summary(pl.UTF-8):	Biblioteki C++ "Boost" - wersja skrośna dla MinGW32
Name:		crossmingw32-%{realname}
Version:	1.44.0
%define	fver	%(echo %{version} | tr . _)
Release:	1
License:	Boost Software License and others
Group:		Development/Libraries
Source0:	http://downloads.sourceforge.net/boost/%{realname}_%{fver}.tar.bz2
# Source0-md5:	f02578f5218f217a9f20e9c30e119c6a
URL:		http://www.boost.org/
BuildRequires:	boost-jam >= 3.1.12
BuildRequires:	crossmingw32-bzip2
BuildRequires:	crossmingw32-gcc-c++
BuildRequires:	crossmingw32-runtime
BuildRequires:	crossmingw32-w32api
BuildRequires:	crossmingw32-zlib
%{?with_serialization:BuildRequires:	wine-programs}
Requires:	crossmingw32-bzip2
Requires:	crossmingw32-runtime
Requires:	crossmingw32-zlib
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		no_install_post_strip	1

%define		target		i386-mingw32
%define		target_platform	i386-pc-mingw32

%define		_sysprefix	/usr
%define		_prefix		%{_sysprefix}/%{target}
%define		_libdir		%{_prefix}/lib
%define		_dlldir		/usr/share/wine/windows/system

%define		__cc		%{target}-gcc
%define		__cxx		%{target}-g++

%ifnarch %{ix86}
# arch-specific flags (like alpha's -mieee) are not valid for i386 gcc
%define		optflags	-O2
%endif

%description
The Boost web site provides free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. One goal is to establish "existing practice" and
provide reference implementations so that the Boost libraries are
suitable for eventual standardization. Some of the libraries have
already been proposed for inclusion in the C++ Standards Committee's
upcoming C++ Standard Library Technical Report.

%description -l pl.UTF-8
Strona http://www.boost.org/ dostarcza darmowe biblioteki C++ wraz z
kodem źródłowym. Nacisk położono na biblioteki, które dobrze
współpracują ze standardową biblioteką C++. Celem jest ustanowienie
"istniejącej praktyki" i dostarczenie implementacji, tak że biblioteki
"Boost" nadają się do ewentualnej standaryzacji. Niektóre z bibliotek
już zostały zgłoszone do komitetu standaryzacyjnego C++ w nadchodzącym
Raporcie Technicznym Biblioteki Standardowej C++.

%package static
Summary:	Static Boost libraries (cross MinGW32 version)
Summary(pl.UTF-8):	Statyczne biblioteki Boost (wersja skrośna MinGW32)
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description static
Static Boost libraries (cross MinGW32 version).

%description static -l pl.UTF-8
Statyczne biblioteki Boost (wersja skrośna MinGW32).

%package dll
Summary:	Boost - DLL libraries for Windows
Summary(pl.UTF-8):	Boost - biblioteki DLL dla Windows
Group:		Applications/Emulators
Requires:	crossmingw32-bzip2-dll
Requires:	crossmingw32-zlib-dll
Requires:	wine

%description dll
Boost - DLL libraries for Windows.

%description dll -l pl.UTF-8
Boost - biblioteki DLL dla Windows.

%prep
%setup -q -n %{realname}_%{fver}

echo 'using gcc : : %{target}-g++ : <cxxflags>"%{rpmcxxflags}"' \
	'<archiver>%{target}-ar ;' >tools/build/v2/user-config.jam

%build
%if %{with serialization}
export WINEPREFIX=`pwd`/wineprefix
install -d wineprefix/drive_c/windows/system32
install %{_prefix}/bin/mingwm10.dll wineprefix/drive_c/windows/system32/
%endif

bjam \
	-d2 \
	--layout=versioned \
	-sBZIP2_BINARY=bzip2 \
	--toolset=gcc \
	--without-python \
	%{!?with_serialization:--without-serialization} \
	--without-test \
	variant=release \
	debug-symbols=on \
	inlining=on \
	link=static,shared \
	target-os=windows \
	threading=multi \
	threadapi=win32

%if 0%{!?debug:1}
%{target}-strip stage/lib/*.dll
%{target}-strip -g -R.comment -R.note stage/lib/*.a
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir},%{_libdir},%{_dlldir}}

cp -r boost $RPM_BUILD_ROOT%{_includedir}
cp -a stage/lib/*.a $RPM_BUILD_ROOT%{_libdir}
install stage/lib/*.dll $RPM_BUILD_ROOT%{_dlldir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_libdir}/libboost_*-mgw*-mt-1_44.dll.a
%{_libdir}/libboost_*-mgw*-mt.dll.a
%{_includedir}/boost

%files static
%defattr(644,root,root,755)
%{_libdir}/libboost_*-mgw*-mt-1_44.a
%{_libdir}/libboost_*-mgw*-mt.a

%files dll
%defattr(644,root,root,755)
%{_dlldir}/libboost_*-mgw*-mt-*.dll
