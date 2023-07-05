#
# Conditional build:
%bcond_without	context		# Boost Context and dependent modules [gas+PE not supported officially by upstream]
%bcond_without	serialization	# Boost Serialization
%bcond_without	test		# Boost Test
#
%define		realname	boost
Summary:	The Boost C++ Libraries - MinGW32 cross version
Summary(pl.UTF-8):	Biblioteki C++ "Boost" - wersja skrośna dla MinGW32
Name:		crossmingw32-%{realname}
Version:	1.82.0
%define	fver	%(echo %{version} | tr . _)
Release:	1
License:	Boost Software License and others
Group:		Development/Libraries
Source0:	https://boostorg.jfrog.io/artifactory/main/release/%{version}/source/%{realname}_%{fver}.tar.bz2
# Source0-md5:	b45dac8b54b58c087bfbed260dbfc03a
Patch0:		boost-allow-mingw32-thread-local.patch
URL:		http://www.boost.org/
BuildRequires:	crossmingw32-bzip2
BuildRequires:	crossmingw32-gcc-c++
BuildRequires:	crossmingw32-runtime
BuildRequires:	crossmingw32-w32api >= 1:5.4.2-2
BuildRequires:	crossmingw32-zlib
Requires:	crossmingw32-bzip2
Requires:	crossmingw32-runtime
Requires:	crossmingw32-zlib
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		no_install_post_strip	1
%define		_enable_debug_packages	0

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

%define		abi_tag		mgw*-mt-x32-1_82

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
%patch0 -p1

echo 'using gcc : : %{target}-g++ : ' \
	'<cxxflags>"%{rpmcxxflags}"' \
	'<archiver>%{target}-ar' \
	'<rc>%{target}-windres ;' >tools/build/src/user-config.jam

# use Windows Message Compiler, not Midnight Commander
%{__sed} -i -e 's,mc $(MCFLAGS),%{target}-windmc $(MCFLAGS),' tools/build/src/tools/mc.jam

%build
./bootstrap.sh --prefix=%{_prefix}
./b2 \
	-d2 \
	%{_smp_mflags} \
	-sBZIP2_BINARY=bzip2 \
	--layout=versioned \
	%{!?with_context:--without-context --without-coroutine --without-coroutine2} \
	--without-python \
	%{!?with_serialization:--without-serialization} \
	%{!?with_test:--without-test} \
	abi=ms \
	address-model=32 \
	binary-format=pe \
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
%{_libdir}/libboost_atomic-%{abi_tag}.dll.a
%{_libdir}/libboost_chrono-%{abi_tag}.dll.a
%{_libdir}/libboost_container-%{abi_tag}.dll.a
%{?with_context:%{_libdir}/libboost_context-%{abi_tag}.dll.a}
%{_libdir}/libboost_contract-%{abi_tag}.dll.a
%{?with_context:%{_libdir}/libboost_coroutine-%{abi_tag}.dll.a}
%{_libdir}/libboost_date_time-%{abi_tag}.dll.a
%{_libdir}/libboost_fiber-%{abi_tag}.dll.a
%{_libdir}/libboost_filesystem-%{abi_tag}.dll.a
%{_libdir}/libboost_graph-%{abi_tag}.dll.a
%{_libdir}/libboost_iostreams-%{abi_tag}.dll.a
%{_libdir}/libboost_json-%{abi_tag}.dll.a
%{_libdir}/libboost_locale-%{abi_tag}.dll.a
%{_libdir}/libboost_log-%{abi_tag}.dll.a
%{_libdir}/libboost_log_setup-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99f-%{abi_tag}.dll.a
%{_libdir}/libboost_math_c99l-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1f-%{abi_tag}.dll.a
%{_libdir}/libboost_math_tr1l-%{abi_tag}.dll.a
%{_libdir}/libboost_nowide-%{abi_tag}.dll.a
%{?with_test:%{_libdir}/libboost_prg_exec_monitor-%{abi_tag}.dll.a}
%{_libdir}/libboost_program_options-%{abi_tag}.dll.a
%{_libdir}/libboost_random-%{abi_tag}.dll.a
%{_libdir}/libboost_regex-%{abi_tag}.dll.a
%{?with_serialization:%{_libdir}/libboost_serialization-%{abi_tag}.dll.a}
%{_libdir}/libboost_stacktrace_basic-%{abi_tag}.dll.a
%{_libdir}/libboost_stacktrace_noop-%{abi_tag}.dll.a
%{_libdir}/libboost_system-%{abi_tag}.dll.a
%{?with_test:%{_libdir}/libboost_test_exec_monitor-%{abi_tag}.a}
%{_libdir}/libboost_thread-%{abi_tag}.dll.a
%{_libdir}/libboost_timer-%{abi_tag}.dll.a
%{_libdir}/libboost_type_erasure-%{abi_tag}.dll.a
%{?with_test:%{_libdir}/libboost_unit_test_framework-%{abi_tag}.dll.a}
%{_libdir}/libboost_url-%{abi_tag}.dll.a
%{_libdir}/libboost_wave-%{abi_tag}.dll.a
%{?with_serialization:%{_libdir}/libboost_wserialization-%{abi_tag}.dll.a}
# static-only
%{_libdir}/libboost_exception-%{abi_tag}.a
%{_includedir}/boost

%files static
%defattr(644,root,root,755)
%{_libdir}/libboost_atomic-%{abi_tag}.a
%{_libdir}/libboost_chrono-%{abi_tag}.a
%{_libdir}/libboost_container-%{abi_tag}.a
%{?with_context:%{_libdir}/libboost_context-%{abi_tag}.a}
%{_libdir}/libboost_contract-%{abi_tag}.a
%{?with_context:%{_libdir}/libboost_coroutine-%{abi_tag}.a}
%{_libdir}/libboost_date_time-%{abi_tag}.a
%{_libdir}/libboost_fiber-%{abi_tag}.a
%{_libdir}/libboost_filesystem-%{abi_tag}.a
%{_libdir}/libboost_graph-%{abi_tag}.a
%{_libdir}/libboost_iostreams-%{abi_tag}.a
%{_libdir}/libboost_json-%{abi_tag}.a
%{_libdir}/libboost_locale-%{abi_tag}.a
%{_libdir}/libboost_log-%{abi_tag}.a
%{_libdir}/libboost_log_setup-%{abi_tag}.a
%{_libdir}/libboost_math_c99-%{abi_tag}.a
%{_libdir}/libboost_math_c99f-%{abi_tag}.a
%{_libdir}/libboost_math_c99l-%{abi_tag}.a
%{_libdir}/libboost_math_tr1-%{abi_tag}.a
%{_libdir}/libboost_math_tr1f-%{abi_tag}.a
%{_libdir}/libboost_math_tr1l-%{abi_tag}.a
%{_libdir}/libboost_nowide-%{abi_tag}.a
%{?with_test:%{_libdir}/libboost_prg_exec_monitor-%{abi_tag}.a}
%{_libdir}/libboost_program_options-%{abi_tag}.a
%{_libdir}/libboost_random-%{abi_tag}.a
%{_libdir}/libboost_regex-%{abi_tag}.a
%{?with_serialization:%{_libdir}/libboost_serialization-%{abi_tag}.a}
%{_libdir}/libboost_stacktrace_basic-%{abi_tag}.a
%{_libdir}/libboost_stacktrace_noop-%{abi_tag}.a
%{_libdir}/libboost_system-%{abi_tag}.a
%{_libdir}/libboost_thread-%{abi_tag}.a
%{_libdir}/libboost_timer-%{abi_tag}.a
%{_libdir}/libboost_type_erasure-%{abi_tag}.a
%{?with_test:%{_libdir}/libboost_unit_test_framework-%{abi_tag}.a}
%{_libdir}/libboost_url-%{abi_tag}.a
%{_libdir}/libboost_wave-%{abi_tag}.a
%{?with_serialization:%{_libdir}/libboost_wserialization-%{abi_tag}.a}

%files dll
%defattr(644,root,root,755)
%{_dlldir}/libboost_atomic-%{abi_tag}.dll
%{_dlldir}/libboost_chrono-%{abi_tag}.dll
%{_dlldir}/libboost_container-%{abi_tag}.dll
%{?with_context:%{_dlldir}/libboost_context-%{abi_tag}.dll}
%{_dlldir}/libboost_contract-%{abi_tag}.dll
%{?with_context:%{_dlldir}/libboost_coroutine-%{abi_tag}.dll}
%{_dlldir}/libboost_date_time-%{abi_tag}.dll
%{_dlldir}/libboost_fiber-%{abi_tag}.dll
%{_dlldir}/libboost_filesystem-%{abi_tag}.dll
%{_dlldir}/libboost_graph-%{abi_tag}.dll
%{_dlldir}/libboost_iostreams-%{abi_tag}.dll
%{_dlldir}/libboost_json-%{abi_tag}.dll
%{_dlldir}/libboost_locale-%{abi_tag}.dll
%{_dlldir}/libboost_log-%{abi_tag}.dll
%{_dlldir}/libboost_log_setup-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99f-%{abi_tag}.dll
%{_dlldir}/libboost_math_c99l-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1f-%{abi_tag}.dll
%{_dlldir}/libboost_math_tr1l-%{abi_tag}.dll
%{_dlldir}/libboost_nowide-%{abi_tag}.dll
%{?with_test:%{_dlldir}/libboost_prg_exec_monitor-%{abi_tag}.dll}
%{_dlldir}/libboost_program_options-%{abi_tag}.dll
%{_dlldir}/libboost_random-%{abi_tag}.dll
%{_dlldir}/libboost_regex-%{abi_tag}.dll
%{?with_serialization:%{_dlldir}/libboost_serialization-%{abi_tag}.dll}
%{_dlldir}/libboost_stacktrace_basic-%{abi_tag}.dll
%{_dlldir}/libboost_stacktrace_noop-%{abi_tag}.dll
%{_dlldir}/libboost_system-%{abi_tag}.dll
%{_dlldir}/libboost_thread-%{abi_tag}.dll
%{_dlldir}/libboost_timer-%{abi_tag}.dll
%{_dlldir}/libboost_type_erasure-%{abi_tag}.dll
%{?with_test:%{_dlldir}/libboost_unit_test_framework-%{abi_tag}.dll}
%{_dlldir}/libboost_url-%{abi_tag}.dll
%{_dlldir}/libboost_wave-%{abi_tag}.dll
%{?with_serialization:%{_dlldir}/libboost_wserialization-%{abi_tag}.dll}
