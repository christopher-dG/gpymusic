# Maintainer: Chris de Graaf <chrisadegraaf@gmail.com>
pkgname=pmcli
pkgver=1.0
pkgrel=1
epoch=
pkgdesc="A lightweight, customizable command-line client for the Google Play Music streaming service."
arch=('any')
url="https://github.com/christopher-dg/pmcli"
license=('MIT')
groups=()
keywords=('media', 'music')
depends=('python>=3.0')
makedepends=()
checkdepends=()
optdepends=()
provides=('pmcli')
conflicts=('pmcli')
replaces=()
backup=('~/.config/pmcli/config')
options=()
install=
changelog=
source=("https://github.com/christopher-dg/$pkgname/archive/$pkgver.tar.gz")
noextract=()
md5sums=("6607f1f178ffdde1b6c260379d9952b3")
validpgpkeys=()

prepare()
{
pip3 install gmusicapi
mkdir -p ~/.{config/$pkgname,local/share/$pkgname/{src,script,playlists}}
}

build()
{
cd "$pkgname-$pkgver"
cp src/*.py ~/.local/share/$pkgname/src
cp config mpv_input.conf ~/.config/$pkgname
}
package()
{
chmod +x ~/.local/share/$pkgname/src/pmcli.py
sudo ln -s ~/.local/share/$pkgname/src/pmcli.py /usr/local/bin/pmcli
}
