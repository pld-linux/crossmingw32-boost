%define		realname	boost
Summary:	The Boost C++ Libraries - Mingw32 cross version
Summary(pl.UTF-8):	Biblioteki C++ "Boost" - wersja skrośna dla Mingw32
Name:		crossmingw32-%{realname}
Version:	1.35.0
%define	fver	%(echo %{version} | tr . _)
Release:	0.1
License:	Boost Software License and others
Group:		Development/Libraries
Source0:	http://dl.sourceforge.net/boost/%{realname}_%{fver}.tar.bz2
# Source0-md5:	dce952a7214e72d6597516bcac84048b
Patch0:		%{name}-win.patch
URL:		http://www.boost.org/
BuildRequires:	boost-jam
BuildRequires:	crossmingw32-bzip2
BuildRequires:	crossmingw32-gcc-c++
BuildRequires:	crossmingw32-runtime
BuildRequires:	crossmingw32-w32api
BuildRequires:	crossmingw32-zlib
BuildRequires:	libtool >= 2:1.4d
BuildRequires:	perl-base
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
Raporcie Technicznym Biblioteki Standardowej C++

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

# - don't know how to pass it through (b)jam -s (no way?)
#   due to oversophisticated build flags system.
%{__perl} -pi -e 's/ -O3 / %{rpmcxxflags} /' tools/build/v2/tools/gcc.jam

sed -i -e 's/#error "wide char i\/o not supported on this platform"//' \
	boost/archive/*.hpp \
	libs/serialization/src/*.cpp \
	libs/serialization/test/*.hpp

%build
CC=%{__cc} ; export CC
CXX=%{__cxx} ; export CXX
LD=%{target}-ld ; export LD
AR=%{target}-ar ; export AR
AS=%{target}-as ; export AS
CROSS_COMPILE=1 ; export CROSS_COMPILE
RANLIB=%{target}-ranlib ; export RANLIB
LDSHARED="%{__cc} -shared" ; export LDSHARED
TARGET="%{target}" ; export TARGET

bjam \
	-q -d2 \
	-sBZIP2_BINARY=bzip2 \
	--toolset=gcc \
	--without-python \
	--without-serialization \
	--without-test \
	variant=release \
	debug-symbols=on \
	inlining=on \
	link=static,shared \
	threading=multi \
	threadapi=win32

mkdir wlib
cd bin.v2/libs
for i in *
do
        cd $i/build/gcc-mingw-*/release/debug-symbols-on/inlining-on
        cd link-static/threadapi-win32/threading-multi
        $AR cru ../../../../../../../../../../../wlib/libboost_$i.a *.o
        $RANLIB ../../../../../../../../../../../wlib/libboost_$i.a

        cd ../../..

        # if there is threading-multi dir 
        # it's content is used for dll and implib
        dll_dir='link-static/threadapi-win32/threading-multi'
        up_dir='../../..'
        if [ -d threading-multi ]; then
                dll_dir='threadapi-win32/threading-multi'
                up_dir='../..'
        fi

        cd $dll_dir

        # libboost_iostreams requires additional
        # libraries
        additional_so_params=
        if [ $i = "iostreams" ]; then
                additional_so_params="-lz.dll -lbzip2.dll"
        fi

        # there are some issuses with dynamic libboost_wave
        if [ $i != "wave" ]; then
                $CXX --shared *.o $additional_so_params \
                        -Wl,--enable-auto-image-base \
                        -o $up_dir/../../../../../../../../wlib/boost_$i.dll \
                        -Wl,--out-implib,libboost_$i.dll.a
                mv libboost_$i.dll.a $up_dir/../../../../../../../../wlib/
        fi

        cd $up_dir/../../../../../..
done
cd ../..

%if 0%{!?debug:1}
%{target}-strip wlib/*.dll
%{target}-strip -g -R.comment -R.note wlib/*.a
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_includedir},%{_libdir},%{_dlldir}}

cp -r boost $RPM_BUILD_ROOT%{_includedir}
install wlib/*.a $RPM_BUILD_ROOT%{_libdir}
install wlib/*.dll $RPM_BUILD_ROOT%{_dlldir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_includedir}/boost
%{_libdir}/*.a

%files dll
%defattr(644,root,root,755)
%{_dlldir}/*.dll
