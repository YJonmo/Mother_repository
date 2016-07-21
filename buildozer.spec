[app]
android.ant_path = /usr/bin
# (str) Title of your application
title = AccelPLot

# (str) Package name
package.name = accelplot

#package.domain = com.wordpress.bytedebugge
package.domain = com.wordpress.bytedebugger
garden_requirements = graph

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = kivy, plyer, ws4py, openssl
orientation = all
fullscreen = 1
[buildozer]
log_level = 2


