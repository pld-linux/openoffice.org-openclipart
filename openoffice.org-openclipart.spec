# TODO
#  - remove use of Xvfb
Summary:	OpenOffice.org clipart from openclipart
Name:		openoffice.org-openclipart
Version:	0.18
Release:	0.1
License:	Creative Commons and/or Public Domain
Group:		Applications/Graphics
BuildRequires:	openclipart-png = 0:%{version}
BuildRequires:	openoffice.org-core
#BuildRequires:	xorg-app-mkfontdir	(missing PreReq in fonts?)
BuildRequires:	xorg-font-font-cursor-misc
BuildRequires:	xorg-font-font-misc-misc-base
BuildRequires:	xorg-xserver-Xvfb
Requires:	openoffice.org-core >= 1:2.1.0-0.m6.5
# same as openoffice.org
ExclusiveArch:	%{ix86} %{x8664} ppc sparc sparcv9
# can't do yet
#BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_ooodir		%{_libdir}/openoffice.org
%define		_gengal		%{_ooodir}/program/gengal
%define		_ooogaldir	%{_ooodir}/share/gallery

%description
OpenOffice.org extra galleries from <http://www.openclipart.org>.

%prep
%setup -q -c -T

%build
OPENCLIPART_DIR=%{_datadir}/openclipart
GAL_BIN=%{_gengal}
GAL_DIR=$(pwd)/gallery
# start number for the new galleries
GAL_NUMBER_FROM=70
XVFB=%{_bindir}/Xvfb

XDISPLAY=98
echo 'Starting Xvfb...'
# try only 10-times to avoid infinite loop
while [ "$XDISPLAY" != 108 ]; do
	if [ ! -f /tmp/.X$XDISPLAY-lock ]; then
		echo "	trying display :$XDISPLAY ..."
		sleep 2s
		$XVFB -ac :$XDISPLAY &
		trap "kill $! > /dev/null 2>&1 || true" EXIT
		# let server to start
		sleep 10s
		if [ -f /tmp/.X$XDISPLAY-lock ]; then
			break
		fi
	fi
	XDISPLAY=$(($XDISPLAY+1))
done

if ! test -f /tmp/.X$XDISPLAY-lock ; then
	echo "Error: Unable to start Xvfb" >&2
	exit 1
fi

export DISPLAY=":$XDISPLAY"
echo "Using DISPLAY="$DISPLAY

rm -rf $GAL_DIR
mkdir -p $GAL_DIR
echo "Building extra galleries from openclipart..."
for dir in $(find -L $OPENCLIPART_DIR -mindepth 1 -maxdepth 1 -type d | sort); do
	# get the gallery name from the directory name
	# and make the first character uppercase
	gal_name=${dir##*/}
	gal_name=$(echo $gal_name | tr '_-' '  ')
	gal_name_rest=${gal_name#?}
	gal_name_first_char=${gal_name%$gal_name_rest}
	gal_name_first_char=$(echo $gal_name_first_char | tr 'a-z' 'A-Z')
	gal_name=$gal_name_first_char$gal_name_rest

	echo "Doing gallery $gal_name..."
	find $dir -name '*.png' -print0 | sort -z | {
		xargs -0 $GAL_BIN \
			--name "$gal_name" \
			--path "$GAL_DIR" \
			--number-from "$GAL_NUMBER_FROM" || exit 1
	}
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_ooogaldir}
cp -a gallery/* $RPM_BUILD_ROOT%{_ooogaldir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_ooogaldir}/*
