%global debug_package %{nil}
Name:           vosk-api
Version:        0.3.45
Release:        1%{?dist}
Summary:        Offline speech recognition toolkit

License:        ASL 2.0
URL:            https://alphacephei.com/vosk
Source0:        https://github.com/alphacep/vosk-api/archive/v%{version}/vosk-api-%{version}.tar.gz
Source1:        https://github.com/alphacep/kaldi/archive/93ef0019b847272a239fbb485ef97f29feb1d587.tar.gz
Source2:        https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
Patch0: kaldi-fst.patch
Patch1: kaldi-lapack.patch
Patch2: kaldi-openblas.patch
Patch3: vosk-lapack.patch
Patch4: vosk-lib_fst.patch
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make

BuildRequires:  blas-static
BuildRequires:  lapack-static
BuildRequires:  openblas-static
BuildRequires:  openfst-tools
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  openblas-devel
BuildRequires:  openfst-devel
BuildRequires:  unzip

%description
Vosk is an offline speech recognition toolkit.

%package -n vosk-model-small-en-us
Summary:        Lightweight English language model

%description -n vosk-model-small-en-us
Lightweight English language model for Vosk.

%prep
%setup -q -a1
tar -xzf %{SOURCE1}


# Move and setup Kaldi
mv kaldi-93ef0019b847272a239fbb485ef97f29feb1d587 kaldi

%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1

cd kaldi/tools
mkdir -p OpenBLAS/install/lib
ln -sf %{_includedir}/openblas OpenBLAS/install/include
ln -sf %{_libdir}/* OpenBLAS/install/lib
mkdir -p openfst/include openfst/lib
ln -sf %{_includedir}/fst openfst/include
ln -sf %{_libdir}/* openfst/lib

%build
cd kaldi/src
#./configure --mathlib=OPENBLAS --shared --use-cuda=no
./configure --mathlib=OPENBLAS_NO_F2C --shared --use-cuda=no
make online2 lm rnnlm

cd %{_builddir}/vosk-api-%{version}/src
make KALDI_ROOT=../kaldi HAVE_OPENBLAS_NO_F2C=1 HAVE_OPENBLAS_CLAPACK=0

%install
# Install vosk-api headers and library
install -Dpm 644 %{_builddir}/vosk-api-%{version}/src/vosk_api.h %{buildroot}%{_includedir}/vosk_api.h
install -Dpm 755 %{_builddir}/vosk-api-%{version}/src/libvosk.so %{buildroot}%{_libdir}/libvosk.so

# Install model
mkdir -p %{buildroot}%{_datadir}/vosk-models
unzip -d %{buildroot}%{_datadir}/vosk-models/ %{SOURCE2}
mv %{buildroot}%{_datadir}/vosk-models/vosk-model-small-en-us-0.15 %{buildroot}%{_datadir}/vosk-models/small-en-us

%check
cd %{_builddir}/vosk-api-%{version}/c
ln -sf %{buildroot}%{_datadir}/vosk-models/small-en-us model
ln -sf ../python/example/test.wav .
make LDFLAGS="-fopenmp -L../src -lvosk -ldl -lpthread -Wl,-rpath,../src"
./test_vosk | grep -q '"text" : "zero one eight zero three"'

%files
%license COPYING
%doc README.md
%{_includedir}/vosk_api.h
%{_libdir}/libvosk.so

%files -n vosk-model-small-en-us
%{_datadir}/vosk-models/

%changelog
* Mon Jul 29 2024 Manish Tiwari <matiwari@redhat.com> - 0.3.45-1
- Initial package

