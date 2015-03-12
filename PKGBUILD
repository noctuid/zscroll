# Maintainer: Lit Wakefield <nocturnalartifice[at]gmail[dot]com>
_pkgname=zscroll
pkgname=zscroll-git
pkgver=
pkgrel=1
pkgdesc="A text scroller for use with panels"
arch=('any')
url="https://github.com/angelic-sedition/zscroll"
license=('Simplified BSD')
depends=('python')
makedepends=('git')
provides=("${_pkgname}")
source=("git://github.com/angelic-sedition/${_pkgname}.git")
md5sums=('SKIP')

pkgver() {
  cd "$srcdir/$_pkgname"
  git describe --long | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
  cd "$srcdir/$_pkgname"
  python setup.py install --root="$pkgdir/" --optimize=1
}
