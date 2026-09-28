# Web de GiraColchón

Web estática de [GiraColchón](https://giracolchon.martinezpenya.es) en castellano, catalán e inglés,
servida por GitHub Pages desde la carpeta `docs/`.

## Estructura

- `build.py`: textos de los tres idiomas y plantillas. Genera todo `docs/`.
- `src/style.css`, `src/img/`, `src/fonts/`: recursos que se copian a `docs/assets/`.
  Las fuentes (Figtree y Fraunces, licencia OFL) se sirven desde la propia web.
- `docs/`: resultado generado. No se edita a mano.

## Generar

```bash
python3 build.py           # web para publicar: sponsors.json vacío y desactivado
python3 build.py --demo    # añade un anuncio de prueba a sponsors.json
```

### Probar el anuncio en el móvil sin publicar

```bash
python3 build.py --demo --base=http://<IP del portátil>:8080
cd docs && python3 -m http.server 8080 --bind 0.0.0.0
# En el repo de la app, APK de debug (permite HTTP solo en debug):
flutter build apk --debug --dart-define=SPONSORS_URL=http://<IP>:8080/sponsors.json
```

La app guarda el catálogo 24 horas. Para ver un cambio antes, borra los datos de la app.

## Publicar una versión nueva de la app

1. En el repo de la app: subir `version` en `pubspec.yaml` y compilar la variante web:
   `flutter build apk --release --flavor web --obfuscate --split-debug-info=build/symbols/<versión>
   --dart-define=SPONSORS_URL=https://giracolchon.martinezpenya.es/sponsors.json`
2. Crear la release `v<versión>` en este repo con el archivo `giracolchon.apk`
   (`app-web-release.apk` renombrado) y su `.sha256`.
3. Actualizar `RELEASE` en `build.py` (versión, build, sha256, tamaño y novedades), ejecutar
   `python3 build.py` y subir. La app avisa a partir de ese momento (lo comprueba cada 12 horas).

Primero la release y después la web: así `version.json` nunca apunta a un archivo que no existe.

## Antes de publicar

- [ ] `python3 build.py` sin `--demo`
- [ ] Crear el alias de correo `contacto@martinezpenya.es`
- [x] Nombre del responsable en la política de privacidad
- [ ] Añadir capturas reales del móvil
- [ ] DNS: `CNAME giracolchon → martinezpenya.github.io`
- [ ] GitHub: Pages desde `main` / `docs`, dominio `giracolchon.martinezpenya.es`, Enforce HTTPS
