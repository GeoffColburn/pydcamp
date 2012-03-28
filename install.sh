#!/usr/bin/env bash

#Installing pipelines.
#Samtools-0.1.6 to build for breakdancer.
#if [ ! -f "extern/samtools-0.1.6/samtools" ]; then
#  pushd extern/samtools-0.1.6/; make; popd
#else
#  echo "Samtools-0.1.6 already compiled."
#fi

##Samtool-0.1.18, newest version.
#if [ -z $(which samtools-0.1.18) ] || [ ! -f "extern/samtools-0.1.18/samtools-0.1.18" ]; then
#  pushd extern/samtools-0.1.18/; 
#  make
#  mv samtools samtools-0.1.18
#  popd
#else
#  echo "Samtools-0.1.18 already installed."
#fi

##Breakdancer.
#if [ -z $(which breakdancer_max) ]; then
#  pushd extern/breakdancer/cpp/;make; popd
#else
#  echo "Breakdancer already installed"
#fi
##Breakdancer dependencies.
##Statistics::Descriptive
#if [ ! -f "~/local/lib/perl5/Statistics/Descriptive.pm" ]; then
#  pushd extern/Statistics-Descriptive-2.6/
#  perl Makefile.PL INSTALL_BASE=~/local
#  make install
#  popd
#else
#  echo "Perl module Statistics::Descriptive already installed."
#fi


./setup.py install --user
./setup.py install --home ~/local
rm -r build
