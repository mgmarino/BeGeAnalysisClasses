#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.


AC_PREREQ(2.50)
AC_INIT([MGMRootClass], [1.0], [mgmarino@uw.edu])
#AC_CONFIG_SRCDIR([MGMRisetimeInfo.hh])
AC_PROG_CXX()
AC_SUBST(CXX)

SOFLAGS="-shared"
MGDOLIBEXTSHARED=so
MYHOST=`uname`
case "${MYHOST}" in
  Darwin*)
  LDFLAGS="-bind_at_load $LDFLAGS" 
  SOFLAGS="-dynamiclib"
  MGDOLIBEXTSHARED=dylib
esac

#Find root
echo ""
echo "${BOLD}Checking for ROOT: ${OFFBOLD} "
m4_include(root.m4)
ROOT_PATH(5.20,, AC_MSG_ERROR(ROOT not found!))

CWD=`pwd`
THISSRCDIR=`basename $CWD`
AC_SUBST(CWD)
AC_SUBST(THISSRCDIR)
AC_SUBST(SOFLAGS)
AC_SUBST(MGDOLIBEXTSHARED)

AC_CONFIG_FILES([
                 LoadMGMClasses.C 
                 buildTools/config.mk
                 ])

AC_OUTPUT
echo 
echo "**********************************************************************************"
echo "**********************************************************************************"
echo
echo "You have successfully configured $PACKAGE_NAME.  Please now compile by issuing the command:"
echo 
echo "     make"
echo 


