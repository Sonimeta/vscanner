[app]
title = V-Scanner UDI
package.name = vscanner
package.domain = org.verifiche.elettriche
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# REQUISITI FONDAMENTALI PER DATAMATRIX E CAMERA
requirements = python3, kivy, requests, camera4kivy, gestures4kivy, pyjnius, pillow

# Permessi Android
android.permissions = CAMERA, INTERNET

# Specifica che vogliamo usare ZBar per la scansione
android.api = 31
android.minapi = 21
android.sdk = 31

# Icona (se ne hai una, altrimenti usa quella di default)
# icon.filename = %(source.dir)s/logo.png

orientation = portrait
fullscreen = 1