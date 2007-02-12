%define		realname	boost
Summary:	The Boost C++ Libraries - Mingw32 cross version
Summary(pl.UTF-8):	Biblioteki C++ "Boost" - wersja skrośna dla Mingw32
Name:		crossmingw32-%{realname}
Version:	1.32.0
%define	_fver	%(echo %{version} | tr . _)
Release:	1
License:	Boost Software License and others
Group:		Libraries
Source0:	http://dl.sourceforge.net/boost/%{realname}_%{_fver}.tar.bz2
# Source0-md5:	e1d1fc7b8fc8c51df4564c2188ca51cb
Patch0:		%{name}-win.patch
URL:		http://www.boost.org/
Requires:	crossmingw32-runtime
BuildRequires:	crossmingw32-gcc-c++
BuildRequires:	crossmingw32-runtime
BuildRequires:	crossmingw32-w32api
BuildRequires:	boost-jam
BuildRequires:	libtool >= 2:1.4d
BuildRequires:	perl-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		no_install_post_strip	1

%define		target		i386-mingw32
%define		target_platform	i386-pc-mingw32
%define		arch		%{_prefix}/%{target}
%define		gccarch		%{_prefix}/lib/gcc-lib/%{target}
%define		gcclib		%{_prefix}/lib/gcc-lib/%{target}/%{version}

%define		__cc		%{target}-gcc
%define		__cxx		%{target}-g++

%ifarch alpha sparc sparc64 sparcv9
# alpha's -mieee and sparc's -mtune=* are not valid for target's gcc
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
Raporcie Technicznym Biblioteki Standardowej C++

%package dll
Summary:	%{realname} - DLL libraries for Windows
Summary(pl.UTF-8):	%{realname} - biblioteki DLL dla Windows
Group:		Applications/Emulators

%description dll
%{realname} - DLL libraries for Windows.

%description dll -l pl.UTF-8
%{realname} - biblioteki DLL dla Windows.

%prep
%setup -q -n %{realname}_%{_fver}
%patch0 -p1

# don't know how to pass it through (b)jam -s (no way?)
# due to oversophisticated build flags system
%{__perl} -pi -e 's/ -O3 / %{rpmcflags} /' tools/build/v1/gcc-tools.jam

%ifarch alpha
# -pthread gcc parameter doesn't add _REENTRANT to cpp macros on alpha (only)
# don't know, is it gcc bug or intentional omission?
# anyway, boost check of -D_REENTRANT in its headers, so it's needed here
%{__perl} -pi -e 's/(CFLAGS.*-pthread)/$1 -D_REENTRANT/' tools/build/v1/gcc-tools.jam
%endif

find . -type f -exec sed -e 's/#error "wide char i\/o not supported on this platform"//' -i \{\} \;

%build
CC=%{target}-gcc ; export CC
CXX=%{target}-g++ ; export CXX
LD=%{target}-ld ; export LD
AR=%{target}-ar ; export AR
AS=%{target}-as ; export AS
CROSS_COMPILE=1 ; export CROSS_COMPILE
CPPFLAGS="-I%{arch}/include" ; export CPPFLAGS
RANLIB=%{target}-ranlib ; export RANLIB
LDSHARED="%{target}-gcc -shared" ; export LDSHARED
TARGET="%{target}" ; export TARGET

PYTHON_ROOT=
PYTHON_VERSION=

bjam \
	-d2 \
	-sBUILD="release <threading>multi" \
	-sPYTHON_ROOT=$PYTHON_ROOT \
	-sPYTHON_VERSION=$PYTHON_VERSION \
	-sGXX="$CXX" \
	-sGCC="$CC"

mkdir wlib
cd bin/*/*
rm -rf test
rm -rf serialization
for i in *
do
	cd $i/*
	lib=`echo lib*so|sed -e 's/\.so//'`
	blib=`echo $lib|sed -e 's/^lib//'`

	cd $lib.a
	find -type f -exec mv \{\} . \;
	$AR cru ../../../../../../wlib/$lib.a *\.o
	$RANLIB ../../../../../../wlib/$lib.a
	cd ..

	cd $lib.so
	find -type f -exec mv \{\} . \;
	%{__cxx} --shared *\.o \
		-Wl,--enable-auto-image-base \
		-o ../../../../../../wlib/$blib.dll \
		-Wl,--out-implib,$lib.dll.a
	mv $lib.dll.a ../../../../../../wlib/
	cd ..

	cd ../..
done
cd ../../..

%if 0%{!?debug:1}
%{target}-strip wlib/*.dll
%{target}-strip -g -R.comment -R.note wlib/*.a
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{arch}/{include,lib}
install -d $RPM_BUILD_ROOT%{_datadir}/wine/windows/system

cp -r boost $RPM_BUILD_ROOT%{arch}/include
install wlib/*.a $RPM_BUILD_ROOT%{arch}/lib
install wlib/*.dll $RPM_BUILD_ROOT%{_datadir}/wine/windows/system/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{arch}/include/boost
%{arch}/lib/*

%files dll
%defattr(644,root,root,755)
%{_datadir}/wine/windows/system/*
