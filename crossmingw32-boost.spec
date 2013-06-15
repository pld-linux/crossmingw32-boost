#
# Conditional build:
%bcond_with	context		# enable Boost Context [crosscompilation problems]
%bcond_with	serialization	# enable Boost Serialization [requires wine hacks]
#
%define		realname	boost
Summary:	The Boost C++ Libraries - MinGW32 cross version
Summary(pl.UTF-8):	Biblioteki C++ "Boost" - wersja skrośna dla MinGW32
Name:		crossmingw32-%{realname}
Version:	1.53.0
%define	fver	%(echo %{version} | tr . _)
Release:	1
License:	Boost Software License and others
Group:		Development/Libraries
Source0:	http://downloads.sourceforge.net/boost/%{realname}_%{fver}.tar.bz2
# Source0-md5:	a00d22605d5dbcfb4c9936a9b35bc4c2
URL:		http://www.boost.org/
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
# -z options are invalid for mingw linker, most of -f options are Linux-specific
%define		filterout_ld	-Wl,-z,.*
%define		filterout_c	-f[-a-z0-9=]*
%define		filterout_cxx	-f[-a-z0-9=]*

%define		abi_tag		1_53

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

./bootstrap.sh --prefix=%{_prefix}
./b2 \
	-d2 \
	%{_smp_mflags} \
	-sBZIP2_BINARY=bzip2 \
	--layout=versioned \
	%{!?with_context:--without-context} \
	--without-python \
	%{!?with_serialization:--without-serialization} \
	--without-test \
	debug-symbols=on \
	inlining=on \
	link=static,shared \
	target-os=windows \
	threadapi=win32 \
	threading=multi \
	toolset=gcc \
	variant=release

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
%{_libdir}/libboost_atomic-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_chrono-mgw*-mt-%{abi_tag}.dll.a
%{?with_context:%{_libdir}/libboost_context-mgw*-mt-%{abi_tag}.dll.a}
%{_libdir}/libboost_date_time-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_filesystem-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_graph-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_iostreams-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_locale-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99f-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99l-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1f-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1l-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_program_options-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_random-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_regex-mgw*-mt-%{abi_tag}.dll.a
%{?with_serialization:%{_libdir}/libboost_serialization-mgw*-mt-%{abi_tag}.dll.a}
%{_libdir}/libboost_signals-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_system-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_thread_win32-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_timer-mgw*-mt-%{abi_tag}.dll.a
%{_libdir}/libboost_wave-mgw*-mt-%{abi_tag}.dll.a
# static-only
%{_libdir}/libboost_exception-mgw*-mt-%{abi_tag}.a
%{_includedir}/boost

%files static
%defattr(644,root,root,755)
%{_libdir}/libboost_atomic-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_chrono-mgw*-mt-%{abi_tag}.a
%{?with_context:%{_libdir}/libboost_context-mgw*-mt-%{abi_tag}.a}
%{_libdir}/libboost_date_time-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_filesystem-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_graph-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_iostreams-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_locale-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_c99-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_c99f-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_c99l-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_tr1-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_tr1f-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_math_tr1l-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_program_options-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_random-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_regex-mgw*-mt-%{abi_tag}.a
%{?with_serialization:%{_libdir}/libboost_serialization-mgw*-mt-%{abi_tag}.a}
%{_libdir}/libboost_signals-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_system-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_thread_win32-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_timer-mgw*-mt-%{abi_tag}.a
%{_libdir}/libboost_wave-mgw*-mt-%{abi_tag}.a

%files dll
%defattr(644,root,root,755)
%{_dlldir}/libboost_atomic-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_chrono-mgw*-mt-%{abi_tag}.dll
%{?with_context:%{_libdir}/libboost_context-mgw*-mt-%{abi_tag}.dll}
%{_dlldir}/libboost_date_time-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_filesystem-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_graph-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_iostreams-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_locale-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99f-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99l-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1f-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1l-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_program_options-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_random-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_regex-mgw*-mt-%{abi_tag}.dll
%{?with_serialization:%{_dlldir}/libboost_serialization-mgw*-mt-%{abi_tag}.dll}
%{_dlldir}/libboost_signals-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_system-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_thread_win32-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_timer-mgw*-mt-%{abi_tag}.dll
%{_dlldir}/libboost_wave-mgw*-mt-%{abi_tag}.dll
