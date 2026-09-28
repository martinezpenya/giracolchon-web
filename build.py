#!/usr/bin/env python3
"""Genera la web estática de GiraColchón en docs/ (lo que sirve GitHub Pages).

Uso: python3 build.py            (web para publicar)
     python3 build.py --demo     (añade un anuncio de prueba a sponsors.json)
     python3 build.py --demo --base=http://192.168.0.102:8080
                                 (la imagen del anuncio se sirve desde otra dirección,
                                 para probar con un servidor local)

Los textos de los tres idiomas están en TEXTS; la estructura, en las
funciones page_*. Todo lo que hay en docs/ se regenera: no se edita a mano.
"""

import json
import shutil
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DOMAIN = "giracolchon.martinezpenya.es"
BASE_URL = f"https://{DOMAIN}"
EMAIL = "contacto@martinezpenya.es"
AUTHOR_SITE = "https://martinezpenya.es"
# El APK se publica en Releases de este repo; «latest» apunta siempre a la última versión.
APK_URL = "https://github.com/martinezpenya/giracolchon-web/releases/latest/download/giracolchon.apk"

# Última versión publicada. La app (variante web) lee docs/version.json para avisar de
# versiones nuevas y comprueba la SHA-256 del APK antes de instalarlo.
# Al publicar una versión: crear la release vX.Y.Z con giracolchon.apk y actualizar esto.
RELEASE = {
    "version": "1.0.1",
    "build": 2,
    "sha256": "90e438c99f56674334d2838fa0296a4f2597f7e3e442dbc5631e1beca39851cb",
    "size": 66096636,
    "notes": {
        "es": "Ahora la app avisa de las versiones nuevas y se actualiza desde la web.",
        "ca": "Ara l'app avisa de les versions noves i s'actualitza des de la web.",
        "en": "The app now tells you about new versions and updates itself from the website.",
    },
}
YEAR = 2026

# Cambia con cada versión de la hoja de estilos para saltarse la caché del navegador.
CSS_VERSION = __import__("hashlib").sha256((ROOT / "src/style.css").read_bytes()).hexdigest()[:10]

LANGS = ["es", "ca", "en"]
# Ruta de cada página por idioma (sin barra inicial; "" = portada).
SLUGS = {
    "home": {"es": "", "ca": "ca/", "en": "en/"},
    "ads": {"es": "anunciate/", "ca": "ca/anuncia-t/", "en": "en/advertise/"},
    "privacy": {"es": "privacidad/", "ca": "ca/privacitat/", "en": "en/privacy/"},
}

# --------------------------------------------------------------------- textos

TEXTS = {
    "es": {
        "nav_how": "Cómo funciona",
        "nav_features": "Funciones",
        "nav_ads": "Anúnciate",
        "nav_privacy": "Privacidad",
        "menu": "Abrir menú",
        "play_soon": "Próximamente en",
        "footer_home": "Inicio",
        "home_title": "GiraColchón · Tu colchón, siempre en su mejor cara",
        "home_desc": "App gratuita para Android que te avisa de cuándo girar o voltear cada colchón, te enseña cómo hacerlo y vigila la garantía.",
        "hero_kicker": "App gratuita para Android",
        "hero_h1": "Tu colchón, siempre en su mejor cara",
        "hero_lead": "GiraColchón te avisa de cuándo toca girar o voltear cada colchón, te enseña cómo hacerlo con una animación y vigila la garantía y la vida útil.",
        "dl_btn": "Descargar APK",
        "dl_small": "Android 8.0 o posterior",
        "dl_kicker": "Descarga",
        "dl_h2": "Instálala ya, mientras llega a Google Play",
        "dl_steps": [
            "Descarga el archivo desde el móvil en el que la vas a usar.",
            "Si Android te lo pide, permite que el navegador instale aplicaciones de origen desconocido.",
            "Abre el archivo y pulsa Instalar.",
        ],
        "dl_note": "La app no se actualiza sola: las versiones nuevas se publican aquí. Cuando esté en Google Play podrás pasarte sin desinstalar y sin perder tus datos.",
        "stats_kicker": "Estadísticas",
        "stats_h2": "Mira cómo cuidas tus colchones",
        "stats_p": "La app lleva la cuenta de cada giro y te enseña si el desgaste se reparte bien entre las cuatro posiciones, para cada colchón o para todos juntos.",
        "stats_items": ["Giros hechos y porcentaje a tiempo", "Retraso medio, racha actual y mejor racha", "Días que ha pasado en cada posición", "Veces en cada posición y giros por mes"],
        "stats_shots": [
            ("estadisticas_resumen_es.png", "Pantalla de estadísticas: 13 giros, 85 % a tiempo, racha de 4 y un gráfico circular del tiempo en cada posición", "Resumen y tiempo en cada posición"),
            ("estadisticas_graficos_es.png", "Gráficos de barras con las veces en cada posición y los giros de cada mes", "Veces en cada posición y giros por mes"),
        ],
        "stats_example": "Capturas de la app con datos de ejemplo de un año.",
        "hero_art_alt": "Dibujo de la app: un colchón volteándose sobre la cama",
        "how_kicker": "Cómo funciona",
        "how_h2": "Tres pasos y te olvidas del calendario",
        "steps": [
            ("Añade tu colchón", "Nombre, medidas y cómo se gira: solo cabeza y pies, con volteo o con cara de invierno y de verano."),
            ("Recibe el aviso", "Cada semana, cada mes o al cambiar de estación, a la hora que elijas. Si se te pasa, te lo recuerda al día siguiente."),
            ("Gira y confirma", "Una animación te enseña qué movimiento toca. Lo confirmas y queda en el historial."),
        ],
        "features_h2": "Todo lo que necesita un colchón para durar más",
        "features": [
            ("bell", "Avisos a tu hora", "Hora de aviso distinta para cada colchón y recordatorio diario si no confirmas."),
            ("rotate", "Rotar y voltear, animado", "La app sugiere el siguiente movimiento para repartir el desgaste entre las cuatro posiciones."),
            ("sun", "Cara de invierno y de verano", "Para colchones con dos caras, te avisa unos días antes de cada cambio de estación."),
            ("shield", "Garantía y vida útil", "Guarda el tique y la garantía, y recibe un aviso antes de que caduque."),
            ("chart", "Estadísticas", "Cuántas veces has girado cada colchón, con qué puntualidad y cuántas veces ha estado en cada posición."),
            ("archive", "Copias de seguridad", "En un ZIP que puedes cifrar y guardar en tu nube: Drive, OneDrive o Nextcloud."),
        ],
        "looks_h2": "Cada colchón, con su propio dibujo",
        "looks_p": "El dibujo sigue las medidas de cada colchón. Elige la forma de la cabecera y los colores para distinguir la cama de matrimonio de la de invitados de un vistazo.",
        "looks": [
            ("single_bars.png", "Colchón individual estrecho con cabecera de barrotes de madera clara", "90 × 190 cm", "cabecera de barrotes"),
            ("king_padded.png", "Colchón ancho y grueso con cabecera acolchada blanca y somier oscuro", "180 × 200 cm", "cabecera acolchada"),
            ("rounded_blue.png", "Colchón de matrimonio con cabecera redondeada azul marino", "135 × 190 cm", "cabecera redondeada"),
        ],
        "priv_kicker": "Privacidad",
        "priv_h2": "Tus datos se quedan en tu móvil",
        "priv_p": "Sin cuentas ni registro. La app funciona sin conexión y no envía tus datos a ningún servidor.",
        "priv_link": "Lee la política de privacidad",
        "priv_checks": [
            ("lock", "Sin cuentas, sin analíticas y sin seguimiento"),
            ("share", "Las copias las compartes tú, donde quieras"),
            ("globe", "En castellano, catalán e inglés, con tema claro y oscuro"),
        ],
        "biz_kicker": "Para empresas",
        "biz_h2": "¿Tu marca es del sector del descanso?",
        "biz_p": "Llega a personas que cuidan su colchón justo cuando se les acaba la garantía o toca renovarlo.",
        "biz_btn": "Anúnciate",
        # Anúnciate
        "ads_title": "Anúnciate en GiraColchón",
        "ads_desc": "Anuncia colchones, almohadas, somieres o ropa de cama a personas que cuidan su descanso, justo cuando más les interesa.",
        "ads_kicker": "Para empresas del sector del descanso",
        "ads_h1": "Llega a quien cuida su descanso, en el momento justo",
        "ads_lead": "Colchones, almohadas, somieres, ropa de cama… Tu oferta aparece dentro de GiraColchón cuando a la persona más le interesa.",
        "ads_btn": "Escríbeme para anunciarte",
        "ads_why": "Por qué anunciarte aquí",
        "benefits": [
            ("target", "Público muy segmentado", "Todos los usuarios tienen al menos un colchón y se preocupan por cuidarlo."),
            ("calendar", "En el momento clave", "Tu oferta aparece cuando se acaba la garantía o la vida útil del colchón, justo cuando toca renovarlo."),
            ("shield", "Discreto y sin rastreo", "Tarjetas propias y respetuosas, sin perfiles de usuario ni redes publicitarias. Tu marca gana confianza."),
            ("translate", "En tres idiomas", "Castellano, catalán e inglés: cada anuncio se muestra en el idioma de la persona."),
        ],
        "ads_where": "Dónde aparece tu anuncio",
        "placements": [
            ("Inicio", "Debajo de la lista de colchones, cada vez que se abre la app."),
            ("Fin de la garantía", "En la ficha del colchón, cuando su garantía está a punto de terminar."),
            ("Fin de la vida útil", "En la ficha, cuando el colchón ha consumido el 90 % de su vida útil."),
            ("Después de girar", "Al confirmar un giro, junto al mensaje de «hecho»."),
        ],
        "ads_where_note": "Tarjetas integradas en la app: nunca a pantalla completa ni en las notificaciones.",
        "ad_caption": "Así se ve la tarjeta en la app",
        "ad_image": "Imagen<br>96 × 96",
        "ad_label": "Patrocinado · Tu marca",
        "ad_title": "El título de tu oferta",
        "ad_text": "Un texto de hasta tres líneas con lo que ofreces.",
        "ad_open": "Ver oferta",
        "ads_need": "Qué necesito para tu campaña",
        "needs": [
            "Nombre de la marca",
            "Título y texto del anuncio, en uno, dos o los tres idiomas",
            "Enlace de destino",
            "Imagen cuadrada (opcional)",
            "Dónde quieres aparecer y fechas de inicio y fin",
        ],
        "ads_rates": "Tarifas",
        "ads_rates_p": "Depende de las ubicaciones y de la duración de la campaña. Escríbeme y te envío las tarifas.",
        "ads_rates_link": "Pide las tarifas por email",
        "ads_talk": "¿Hablamos?",
        "ads_talk_p": "Cuéntame qué vendes y buscamos juntos el mejor momento para enseñarlo.",
        "mail_subject": "Anunciarse en GiraColchón",
        "mail_rates_subject": "Tarifas de GiraColchón",
        "mail_body": "Empresa:\nProducto:\nWeb:\nFechas de la campaña:\n",
        # Privacidad
        "privacy_title": "Política de privacidad · GiraColchón",
        "privacy_desc": "Política de privacidad de GiraColchón: sin cuentas, sin datos personales y todo guardado en tu móvil.",
        "privacy_h1": "Política de privacidad",
        "updated": "Última actualización: 28 de septiembre de 2026",
        "toc": "En esta página",
        "summary": "<strong>En resumen:</strong> GiraColchón no tiene cuentas, no recoge datos personales y guarda todo lo que introduces solo en tu móvil.",
        "legal": [
            ("responsable", "Responsable", [
                "David Martínez Peña, desarrollador de la app. Contacto: {mail}.",
            ]),
            ("datos", "Datos que guarda la app", [
                "Los colchones, sus medidas, el historial de giros, los ajustes y las fotos o documentos que adjuntas se guardan en el almacenamiento interno del móvil. No se envían a ningún servidor.",
                "Si tienes activada la copia de seguridad de Android, el sistema puede incluir estos datos en la copia de tu cuenta de Google, según la configuración de tu teléfono.",
            ]),
            ("copias", "Copias de seguridad", [
                "La app crea copias en un archivo ZIP, que puedes proteger con contraseña. Tú decides si lo compartes y dónde lo guardas (Drive, OneDrive, Nextcloud u otro servicio). El tratamiento en ese servicio lo rige su propia política.",
            ]),
            ("anuncios", "Anuncios de patrocinadores", [
                "Para mostrar ofertas, la app descarga como mucho una vez al día un catálogo público desde {domain}. La petición no incluye ningún identificador tuyo ni datos de tus colchones. Como en cualquier conexión a internet, el servidor recibe la dirección IP del móvil.",
                "No hay redes publicitarias ni perfiles. Si abres un anuncio, se abre la web del anunciante en tu navegador, con su propia política.",
            ]),
            ("permisos", "Permisos", [
                ["<strong>Notificaciones y alarmas exactas:</strong> para avisarte a la hora que elijas.",
                 "<strong>Inicio del dispositivo:</strong> para volver a programar los avisos después de reiniciar.",
                 "<strong>Internet:</strong> solo para el catálogo de anuncios.",
                 "<strong>Fotos y documentos:</strong> solo los que eliges tú desde el selector del sistema."],
            ]),
            ("derechos", "Tus derechos", [
                "Como no tratamos datos personales, no hay nada que consultar, corregir ni borrar en nuestros servidores. Para borrar tus datos, desinstala la app o bórralos desde los ajustes de Android. Para cualquier duda, escribe a {mail}.",
            ]),
            ("web", "Esta web", [
                "Esta web está alojada en GitHub Pages y el APK se descarga desde GitHub Releases. GitHub recibe la dirección IP de quien visita la web o descarga el archivo. No usa cookies, analíticas ni fuentes de terceros.",
            ]),
            ("cambios", "Cambios", [
                "Si esta política cambia, se publicará aquí con una nueva fecha de actualización.",
            ]),
        ],
    },
    "ca": {
        "nav_how": "Com funciona",
        "nav_features": "Funcions",
        "nav_ads": "Anuncia't",
        "nav_privacy": "Privacitat",
        "menu": "Obri el menú",
        "play_soon": "Prompte a",
        "footer_home": "Inici",
        "home_title": "GiraColchón · El teu matalàs, sempre per la seua millor cara",
        "home_desc": "App gratuïta per a Android que t'avisa de quan cal girar o voltejar cada matalàs, t'ensenya com fer-ho i vigila la garantia.",
        "hero_kicker": "App gratuïta per a Android",
        "hero_h1": "El teu matalàs, sempre per la seua millor cara",
        "hero_lead": "GiraColchón t'avisa de quan toca girar o voltejar cada matalàs, t'ensenya com fer-ho amb una animació i vigila la garantia i la vida útil.",
        "dl_btn": "Descarrega l'APK",
        "dl_small": "Android 8.0 o posterior",
        "dl_kicker": "Descàrrega",
        "dl_h2": "Instal·la-la ja, mentre arriba a Google Play",
        "dl_steps": [
            "Descarrega l'arxiu des del mòbil en què la faràs servir.",
            "Si Android t'ho demana, permet que el navegador instal·le aplicacions d'origen desconegut.",
            "Obri l'arxiu i prem Instal·la.",
        ],
        "dl_note": "L'app no s'actualitza sola: les versions noves es publiquen ací. Quan estiga a Google Play podràs passar-t'hi sense desinstal·lar i sense perdre les teues dades.",
        "stats_kicker": "Estadístiques",
        "stats_h2": "Mira com cuides els teus matalassos",
        "stats_p": "L'app porta el compte de cada gir i t'ensenya si el desgast es reparteix bé entre les quatre posicions, per a cada matalàs o per a tots junts.",
        "stats_items": ["Girs fets i percentatge a temps", "Retard mitjà, ratxa actual i millor ratxa", "Dies que ha passat en cada posició", "Vegades en cada posició i girs per mes"],
        "stats_shots": [
            ("estadisticas_resumen_ca.png", "Pantalla d'estadístiques: 13 girs, 85 % a temps, ratxa de 4 i un gràfic circular del temps en cada posició", "Resum i temps en cada posició"),
            ("estadisticas_graficos_ca.png", "Gràfics de barres amb les vegades en cada posició i els girs de cada mes", "Vegades en cada posició i girs per mes"),
        ],
        "stats_example": "Captures de l'app amb dades d'exemple d'un any.",
        "hero_art_alt": "Dibuix de l'app: un matalàs que es volteja sobre el llit",
        "how_kicker": "Com funciona",
        "how_h2": "Tres passos i t'oblides del calendari",
        "steps": [
            ("Afig el teu matalàs", "Nom, mides i com es gira: només cap i peus, amb volteig o amb cara d'hivern i d'estiu."),
            ("Rep l'avís", "Cada setmana, cada mes o en canviar d'estació, a l'hora que tries. Si se't passa, t'ho recorda l'endemà."),
            ("Gira i confirma", "Una animació t'ensenya quin moviment toca. Ho confirmes i queda en l'historial."),
        ],
        "features_h2": "Tot el que necessita un matalàs per a durar més",
        "features": [
            ("bell", "Avisos a la teua hora", "Hora d'avís diferent per a cada matalàs i recordatori diari si no confirmes."),
            ("rotate", "Rotar i voltejar, animat", "L'app suggereix el moviment següent per a repartir el desgast entre les quatre posicions."),
            ("sun", "Cara d'hivern i d'estiu", "Per a matalassos amb dues cares, t'avisa uns dies abans de cada canvi d'estació."),
            ("shield", "Garantia i vida útil", "Guarda el tiquet i la garantia, i rep un avís abans que caduque."),
            ("chart", "Estadístiques", "Quantes vegades has girat cada matalàs, amb quina puntualitat i quantes vegades ha estat en cada posició."),
            ("archive", "Còpies de seguretat", "En un ZIP que pots xifrar i guardar en el teu núvol: Drive, OneDrive o Nextcloud."),
        ],
        "looks_h2": "Cada matalàs, amb el seu propi dibuix",
        "looks_p": "El dibuix segueix les mides de cada matalàs. Tria la forma del capçal i els colors per a distingir el llit de matrimoni del de convidats d'un colp d'ull.",
        "looks": [
            ("single_bars.png", "Matalàs individual estret amb capçal de barrots de fusta clara", "90 × 190 cm", "capçal de barrots"),
            ("king_padded.png", "Matalàs ample i gruixut amb capçal encoixinat blanc i somier fosc", "180 × 200 cm", "capçal encoixinat"),
            ("rounded_blue.png", "Matalàs de matrimoni amb capçal arrodonit blau marí", "135 × 190 cm", "capçal arrodonit"),
        ],
        "priv_kicker": "Privacitat",
        "priv_h2": "Les teues dades es queden al teu mòbil",
        "priv_p": "Sense comptes ni registre. L'app funciona sense connexió i no envia les teues dades a cap servidor.",
        "priv_link": "Llig la política de privacitat",
        "priv_checks": [
            ("lock", "Sense comptes, sense analítiques i sense seguiment"),
            ("share", "Les còpies les comparteixes tu, on vulgues"),
            ("globe", "En castellà, català i anglés, amb tema clar i fosc"),
        ],
        "biz_kicker": "Per a empreses",
        "biz_h2": "La teua marca és del sector del descans?",
        "biz_p": "Arriba a persones que cuiden el seu matalàs just quan se'ls acaba la garantia o toca renovar-lo.",
        "biz_btn": "Anuncia't",
        "ads_title": "Anuncia't a GiraColchón",
        "ads_desc": "Anuncia matalassos, coixins, somiers o roba de llit a persones que cuiden el seu descans, just quan més els interessa.",
        "ads_kicker": "Per a empreses del sector del descans",
        "ads_h1": "Arriba a qui cuida el seu descans, en el moment just",
        "ads_lead": "Matalassos, coixins, somiers, roba de llit… La teua oferta apareix dins de GiraColchón quan a la persona més li interessa.",
        "ads_btn": "Escriu-me per a anunciar-te",
        "ads_why": "Per què anunciar-te ací",
        "benefits": [
            ("target", "Públic molt segmentat", "Tots els usuaris tenen almenys un matalàs i es preocupen de cuidar-lo."),
            ("calendar", "En el moment clau", "La teua oferta apareix quan s'acaba la garantia o la vida útil del matalàs, just quan toca renovar-lo."),
            ("shield", "Discret i sense rastreig", "Targetes pròpies i respectuoses, sense perfils d'usuari ni xarxes publicitàries. La teua marca guanya confiança."),
            ("translate", "En tres idiomes", "Castellà, català i anglés: cada anunci es mostra en l'idioma de la persona."),
        ],
        "ads_where": "On apareix el teu anunci",
        "placements": [
            ("Inici", "Davall de la llista de matalassos, cada vegada que s'obri l'app."),
            ("Fi de la garantia", "En la fitxa del matalàs, quan la seua garantia està a punt d'acabar."),
            ("Fi de la vida útil", "En la fitxa, quan el matalàs ha consumit el 90 % de la seua vida útil."),
            ("Després de girar", "En confirmar un gir, al costat del missatge de «fet»."),
        ],
        "ads_where_note": "Targetes integrades en l'app: mai a pantalla completa ni en les notificacions.",
        "ad_caption": "Així es veu la targeta en l'app",
        "ad_image": "Imatge<br>96 × 96",
        "ad_label": "Patrocinat · La teua marca",
        "ad_title": "El títol de la teua oferta",
        "ad_text": "Un text de fins a tres línies amb el que oferixes.",
        "ad_open": "Veure oferta",
        "ads_need": "Què necessite per a la teua campanya",
        "needs": [
            "Nom de la marca",
            "Títol i text de l'anunci, en un, dos o els tres idiomes",
            "Enllaç de destinació",
            "Imatge quadrada (opcional)",
            "On vols aparéixer i dates d'inici i fi",
        ],
        "ads_rates": "Tarifes",
        "ads_rates_p": "Depén de les ubicacions i de la durada de la campanya. Escriu-me i t'envie les tarifes.",
        "ads_rates_link": "Demana les tarifes per correu",
        "ads_talk": "En parlem?",
        "ads_talk_p": "Conta'm què vens i busquem junts el millor moment per a ensenyar-ho.",
        "mail_subject": "Anunciar-se a GiraColchón",
        "mail_rates_subject": "Tarifes de GiraColchón",
        "mail_body": "Empresa:\nProducte:\nWeb:\nDates de la campanya:\n",
        "privacy_title": "Política de privacitat · GiraColchón",
        "privacy_desc": "Política de privacitat de GiraColchón: sense comptes, sense dades personals i tot guardat al teu mòbil.",
        "privacy_h1": "Política de privacitat",
        "updated": "Última actualització: 28 de setembre de 2026",
        "toc": "En esta pàgina",
        "summary": "<strong>En resum:</strong> GiraColchón no té comptes, no arreplega dades personals i guarda tot el que introduïxes només al teu mòbil.",
        "legal": [
            ("responsable", "Responsable", [
                "David Martínez Peña, desenvolupador de l'app. Contacte: {mail}.",
            ]),
            ("dades", "Dades que guarda l'app", [
                "Els matalassos, les seues mides, l'historial de girs, els ajustos i les fotos o documents que adjuntes es guarden en l'emmagatzematge intern del mòbil. No s'envien a cap servidor.",
                "Si tens activada la còpia de seguretat d'Android, el sistema pot incloure estes dades en la còpia del teu compte de Google, segons la configuració del teu telèfon.",
            ]),
            ("copies", "Còpies de seguretat", [
                "L'app crea còpies en un arxiu ZIP, que pots protegir amb contrasenya. Tu decidixes si el comparteixes i on el guardes (Drive, OneDrive, Nextcloud o un altre servei). El tractament en eixe servei el regix la seua pròpia política.",
            ]),
            ("anuncis", "Anuncis de patrocinadors", [
                "Per a mostrar ofertes, l'app descarrega com a molt una vegada al dia un catàleg públic des de {domain}. La petició no inclou cap identificador teu ni dades dels teus matalassos. Com en qualsevol connexió a internet, el servidor rep l'adreça IP del mòbil.",
                "No hi ha xarxes publicitàries ni perfils. Si obris un anunci, s'obri la web de l'anunciant en el teu navegador, amb la seua pròpia política.",
            ]),
            ("permisos", "Permisos", [
                ["<strong>Notificacions i alarmes exactes:</strong> per a avisar-te a l'hora que tries.",
                 "<strong>Inici del dispositiu:</strong> per a tornar a programar els avisos després de reiniciar.",
                 "<strong>Internet:</strong> només per al catàleg d'anuncis.",
                 "<strong>Fotos i documents:</strong> només els que tries tu des del selector del sistema."],
            ]),
            ("drets", "Els teus drets", [
                "Com que no tractem dades personals, no hi ha res a consultar, corregir ni esborrar en els nostres servidors. Per a esborrar les teues dades, desinstal·la l'app o esborra-les des dels ajustos d'Android. Per a qualsevol dubte, escriu a {mail}.",
            ]),
            ("web", "Esta web", [
                "Esta web està allotjada en GitHub Pages i l'APK es descarrega des de GitHub Releases. GitHub rep l'adreça IP de qui visita la web o descarrega l'arxiu. No usa galetes, analítiques ni fonts de tercers.",
            ]),
            ("canvis", "Canvis", [
                "Si esta política canvia, es publicarà ací amb una nova data d'actualització.",
            ]),
        ],
    },
    "en": {
        "nav_how": "How it works",
        "nav_features": "Features",
        "nav_ads": "Advertise",
        "nav_privacy": "Privacy",
        "menu": "Open menu",
        "play_soon": "Coming soon to",
        "footer_home": "Home",
        "home_title": "GiraColchón · Your mattress, always on its best side",
        "home_desc": "Free Android app that reminds you when to turn or flip each mattress, shows you how and keeps track of the warranty.",
        "hero_kicker": "Free app for Android",
        "hero_h1": "Your mattress, always on its best side",
        "hero_lead": "GiraColchón reminds you when each mattress needs turning or flipping, shows you how with an animation and keeps track of warranty and lifespan.",
        "dl_btn": "Download APK",
        "dl_small": "Android 8.0 or later",
        "dl_kicker": "Download",
        "dl_h2": "Install it now, while it makes its way to Google Play",
        "dl_steps": [
            "Download the file on the phone you will use it on.",
            "If Android asks, allow your browser to install apps from unknown sources.",
            "Open the file and tap Install.",
        ],
        "dl_note": "The app does not update itself: new versions are published here. Once it is on Google Play you can switch without uninstalling or losing your data.",
        "stats_kicker": "Statistics",
        "stats_h2": "See how well you look after your mattresses",
        "stats_p": "The app counts every turn and shows whether wear is spread evenly across the four positions, for each mattress or all of them together.",
        "stats_items": ["Turns done and share on time", "Average delay, current streak and best streak", "Days spent in each position", "Times in each position and turns per month"],
        "stats_shots": [
            ("estadisticas_resumen_en.png", "Statistics screen: 13 turns, 85% on time, a streak of 4 and a donut chart of time in each position", "Summary and time in each position"),
            ("estadisticas_graficos_en.png", "Bar charts of times in each position and turns per month", "Times in each position and turns per month"),
        ],
        "stats_example": "Screenshots of the app with a year of sample data.",
        "hero_art_alt": "Drawing from the app: a mattress flipping over on the bed",
        "how_kicker": "How it works",
        "how_h2": "Three steps and you can forget the calendar",
        "steps": [
            ("Add your mattress", "Name, size and how it is turned: head to foot only, with flipping, or with a winter and a summer side."),
            ("Get the reminder", "Every week, every month or when the season changes, at the time you choose. If you miss it, it reminds you the next day."),
            ("Turn it and confirm", "An animation shows you which move is next. Confirm it and it goes into the history."),
        ],
        "features_h2": "Everything a mattress needs to last longer",
        "features": [
            ("bell", "Reminders at your time", "A different reminder time for each mattress and a daily reminder if you do not confirm."),
            ("rotate", "Animated turning and flipping", "The app suggests the next move to spread wear across the four positions."),
            ("sun", "Winter and summer sides", "For two-sided mattresses, it reminds you a few days before each change of season."),
            ("shield", "Warranty and lifespan", "Keep the receipt and warranty, and get a reminder before it expires."),
            ("chart", "Statistics", "How many times you have turned each mattress, how punctually and how often it has been in each position."),
            ("archive", "Backups", "In a ZIP you can encrypt and keep in your cloud: Drive, OneDrive or Nextcloud."),
        ],
        "looks_h2": "Every mattress with its own drawing",
        "looks_p": "The drawing follows each mattress's size. Choose the headboard shape and colours to tell the double bed from the guest bed at a glance.",
        "looks": [
            ("single_bars.png", "Narrow single mattress with a light wood bar headboard", "90 × 190 cm", "bar headboard"),
            ("king_padded.png", "Wide, thick mattress with a white padded headboard and dark base", "180 × 200 cm", "padded headboard"),
            ("rounded_blue.png", "Double mattress with a rounded navy headboard", "135 × 190 cm", "rounded headboard"),
        ],
        "priv_kicker": "Privacy",
        "priv_h2": "Your data stays on your phone",
        "priv_p": "No accounts, no sign-up. The app works offline and does not send your data to any server.",
        "priv_link": "Read the privacy policy",
        "priv_checks": [
            ("lock", "No accounts, no analytics, no tracking"),
            ("share", "You share your backups, wherever you like"),
            ("globe", "In Spanish, Catalan and English, with light and dark themes"),
        ],
        "biz_kicker": "For businesses",
        "biz_h2": "Is your brand in the sleep industry?",
        "biz_p": "Reach people who look after their mattress right when the warranty runs out or it is time to replace it.",
        "biz_btn": "Advertise",
        "ads_title": "Advertise on GiraColchón",
        "ads_desc": "Advertise mattresses, pillows, bed bases or bedding to people who care about their sleep, right when it matters most to them.",
        "ads_kicker": "For businesses in the sleep industry",
        "ads_h1": "Reach people who care about their sleep, at the right moment",
        "ads_lead": "Mattresses, pillows, bed bases, bedding… Your offer appears inside GiraColchón when it matters most to the person.",
        "ads_btn": "Email me to advertise",
        "ads_why": "Why advertise here",
        "benefits": [
            ("target", "Highly targeted audience", "Every user owns at least one mattress and cares about looking after it."),
            ("calendar", "At the key moment", "Your offer appears when the mattress warranty or lifespan ends, just when it is time to replace it."),
            ("shield", "Discreet and tracking-free", "Our own respectful cards, with no user profiling or ad networks. Your brand earns trust."),
            ("translate", "In three languages", "Spanish, Catalan and English: each ad is shown in the user's language."),
        ],
        "ads_where": "Where your ad appears",
        "placements": [
            ("Home", "Below the list of mattresses, every time the app opens."),
            ("Warranty ending", "On the mattress page, when its warranty is about to end."),
            ("Lifespan ending", "On the mattress page, when the mattress has used 90% of its lifespan."),
            ("After turning", "When a turn is confirmed, next to the “done” message."),
        ],
        "ads_where_note": "Cards built into the app: never full screen and never in notifications.",
        "ad_caption": "This is how the card looks in the app",
        "ad_image": "Image<br>96 × 96",
        "ad_label": "Sponsored · Your brand",
        "ad_title": "Your offer's title",
        "ad_text": "Up to three lines of text about what you offer.",
        "ad_open": "See offer",
        "ads_need": "What I need for your campaign",
        "needs": [
            "Brand name",
            "Ad title and text, in one, two or all three languages",
            "Destination link",
            "Square image (optional)",
            "Where you want to appear, plus start and end dates",
        ],
        "ads_rates": "Rates",
        "ads_rates_p": "Rates depend on placements and campaign length. Email me and I will send them to you.",
        "ads_rates_link": "Ask for rates by email",
        "ads_talk": "Shall we talk?",
        "ads_talk_p": "Tell me what you sell and we will find the best moment to show it together.",
        "mail_subject": "Advertising on GiraColchón",
        "mail_rates_subject": "GiraColchón rates",
        "mail_body": "Company:\nProduct:\nWebsite:\nCampaign dates:\n",
        "privacy_title": "Privacy policy · GiraColchón",
        "privacy_desc": "GiraColchón privacy policy: no accounts, no personal data, everything stored on your phone.",
        "privacy_h1": "Privacy policy",
        "updated": "Last updated: 28 September 2026",
        "toc": "On this page",
        "summary": "<strong>In short:</strong> GiraColchón has no accounts, collects no personal data and keeps everything you enter on your phone only.",
        "legal": [
            ("controller", "Data controller", [
                "David Martínez Peña, developer of the app. Contact: {mail}.",
            ]),
            ("data", "Data the app stores", [
                "Your mattresses, their sizes, the turning history, settings and any photos or documents you attach are stored in the phone's internal storage. They are not sent to any server.",
                "If Android backup is turned on, the system may include this data in your Google account backup, depending on your phone's settings.",
            ]),
            ("backups", "Backups", [
                "The app creates backups as a ZIP file, which you can protect with a password. You decide whether to share it and where to keep it (Drive, OneDrive, Nextcloud or another service). That service's own policy applies there.",
            ]),
            ("ads", "Sponsor ads", [
                "To show offers, the app downloads a public catalogue from {domain} at most once a day. The request contains no identifier of yours and no data about your mattresses. As with any internet connection, the server receives the phone's IP address.",
                "There are no ad networks and no profiling. If you open an ad, the advertiser's website opens in your browser, under its own policy.",
            ]),
            ("permissions", "Permissions", [
                ["<strong>Notifications and exact alarms:</strong> to remind you at the time you choose.",
                 "<strong>Device start-up:</strong> to reschedule reminders after a restart.",
                 "<strong>Internet:</strong> only for the ad catalogue.",
                 "<strong>Photos and documents:</strong> only the ones you pick in the system picker."],
            ]),
            ("rights", "Your rights", [
                "As we process no personal data, there is nothing on our servers to access, correct or delete. To delete your data, uninstall the app or clear it from Android settings. For any questions, email {mail}.",
            ]),
            ("website", "This website", [
                "This website is hosted on GitHub Pages and the APK is downloaded from GitHub Releases. GitHub receives the IP address of anyone who visits the site or downloads the file. It uses no cookies, analytics or third-party fonts.",
            ]),
            ("changes", "Changes", [
                "If this policy changes, the new version will be published here with a new date.",
            ]),
        ],
    },
}

# Anuncio sintético para probar las tarjetas en la app (solo con --demo).
DEMO_CAMPAIGN = {
    "id": "demo-2026",
    "sponsor": "Marca de prueba",
    "title": {
        "es": "Anuncio de prueba: almohada viscoelástica",
        "ca": "Anunci de prova: coixí viscoelàstic",
        "en": "Test ad: memory foam pillow",
    },
    "body": {
        "es": "Esto es un anuncio sintético para ver cómo queda la tarjeta de patrocinio en GiraColchón.",
        "ca": "Açò és un anunci sintètic per a veure com queda la targeta de patrocini en GiraColchón.",
        "en": "This is a synthetic ad to see how the sponsor card looks in GiraColchón.",
    },
    "url": f"{BASE_URL}/anunciate/",
    "placements": ["home", "warrantyEnding", "lifespanEnding", "afterRotation"],
    "tags": ["demo"],
}

# ---------------------------------------------------------------------- iconos

def svg(paths, size=28, color="#4a5fa8", width=1.7):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')

ICONS = {
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
    "rotate": '<path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 21v-5h5"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "archive": '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9"/><path d="M10 13h4"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "share": '<path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M16 6l-4-4-4 4"/><path d="M12 2v13"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/><path d="M9 15l2 2 4-4"/>',
    "translate": '<path d="M4 5h9M8.5 3v2M6 5c0 4 3 7 6 8M11 5c0 4-3 8-7 9"/><path d="M13 21l4-9 4 9M14.5 18h5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "download": '<path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/>',
}

# ----------------------------------------------------------------- plantillas

def rel(from_slug, to_slug):
    """Ruta relativa entre dos páginas (funciona con o sin dominio propio)."""
    depth = from_slug.count("/")
    return "../" * depth + to_slug if (to_slug or depth) else "./"


def mailto(subject, body=None):
    from urllib.parse import quote
    q = f"subject={quote(subject)}"
    if body:
        q += f"&body={quote(body)}"
    return escape(f"mailto:{EMAIL}?{q}")


def layout(lang, page, title, desc, hero, main):
    t = TEXTS[lang]
    slug = SLUGS[page][lang]
    a = lambda p: rel(slug, SLUGS[p][lang])  # noqa: E731
    asset = lambda f: rel(slug, "assets/" + f)  # noqa: E731
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{BASE_URL}/{SLUGS[page][l]}">' for l in LANGS
    )
    lang_links = "".join(
        f'<a href="{rel(slug, SLUGS[page][l])}" hreflang="{l}" lang="{l}"'
        + (' aria-current="true"' if l == lang else "")
        + f">{l.upper()}</a>"
        for l in LANGS
    )
    cur = lambda p: ' aria-current="page"' if p == page else ""  # noqa: E731
    nav = (
        f'<a href="{a("home")}#como-funciona">{t["nav_how"]}</a>'
        f'<a href="{a("home")}#funciones">{t["nav_features"]}</a>'
        f'<a href="{a("ads")}"{cur("ads")}>{t["nav_ads"]}</a>'
        f'<a href="{a("privacy")}"{cur("privacy")}>{t["nav_privacy"]}</a>'
        f'<div class="lang">{lang_links}</div>'
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{BASE_URL}/{slug}">
{alternates}
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{BASE_URL}/assets/img/icono.png">
<meta name="theme-color" content="#2e3a73">
<link rel="icon" type="image/png" href="{asset('img/favicon.png')}">
<link rel="apple-touch-icon" href="{asset('img/apple-touch-icon.png')}">
<link rel="stylesheet" href="{asset('style.css')}?v={CSS_VERSION}">
</head>
<body>
<section class="hero">
<div class="wrap">
<header class="topbar">
<a class="brand" href="{a('home')}"><img src="{asset('img/icono.png')}" alt="" width="44" height="44">GiraColchón</a>
<nav class="nav" aria-label="Principal">{nav}</nav>
<details class="menu"><summary aria-label="{t['menu']}">{svg(ICONS['menu'], 26, '#ffffff', 2)}</summary><nav class="nav" aria-label="Principal">{nav}</nav></details>
</header>
{hero}
</div>
</section>
<main>
{main}
</main>
<footer class="footer">
<div class="wrap">
<div class="footer-brand"><img src="{asset('img/icono.png')}" alt="" width="32" height="32"><span>© {YEAR} GiraColchón · <a href="{AUTHOR_SITE}">martinezpenya.es</a></span></div>
<nav aria-label="Pie">
<a href="{a('home')}">{t['footer_home']}</a>
<a href="{a('ads')}">{t['nav_ads']}</a>
<a href="{a('privacy')}">{t['nav_privacy']}</a>
<a href="mailto:{EMAIL}">{EMAIL}</a>
</nav>
</div>
</footer>
</body>
</html>
"""


def page_home(lang):
    t = TEXTS[lang]
    slug = SLUGS["home"][lang]
    asset = lambda f: rel(slug, "assets/" + f)  # noqa: E731
    hero = f"""<div class="hero-body">
<div class="stack" style="gap:26px">
<div class="kicker">{t['hero_kicker']}</div>
<h1>{t['hero_h1']}</h1>
<p class="lead">{t['hero_lead']}</p>
<div class="actions">
<a class="btn btn-light" href="{APK_URL}">{svg(ICONS['download'], 24, '#2e3a73', 1.9)}<span class="btn-2l"><small>{t['dl_small']}</small><span>{t['dl_btn']}</span></span></a>
<span class="btn btn-play" aria-disabled="true"><span class="btn-2l"><small>{t['play_soon']}</small><span>Google Play</span></span></span>
</div>
</div>
<div class="hero-art"><img src="{asset('img/flip_mid.png')}" alt="{escape(t['hero_art_alt'])}" width="400" height="280"></div>
</div>"""
    steps = "".join(
        f'<li class="card"><div class="num">{i}</div><h3>{h}</h3><p class="muted">{p}</p></li>'
        for i, (h, p) in enumerate(t["steps"], 1)
    )
    features = "".join(
        f'<div class="feature">{svg(ICONS[ic], 30)}<div><h3>{h}</h3><p class="muted">{p}</p></div></div>'
        for ic, h, p in t["features"]
    )
    looks = "".join(
        f'<figure><img src="{asset("img/" + f)}" alt="{escape(alt)}" width="400" height="280" loading="lazy">'
        f'<figcaption class="muted"><strong style="color:var(--ink)">{size}</strong> · {cap}</figcaption></figure>'
        for f, alt, size, cap in t["looks"]
    )
    stats_items = "".join(
        f"<li>{svg(ICONS['chart'], 22, '#4a5fa8', 1.8)}{x}</li>" for x in t["stats_items"]
    )
    stats_shots = "".join(
        f'<figure><div class="shot"><img src="{asset("img/" + f)}" alt="{escape(alt)}" width="412" '
        f'height="{525 if "resumen" in f else 430}" loading="lazy"></div><figcaption class="muted">{cap}</figcaption></figure>'
        for f, alt, cap in t["stats_shots"]
    )
    checks = "".join(f"<li>{svg(ICONS[ic], 24, '#4a5fa8', 1.8)}{txt}</li>" for ic, txt in t["priv_checks"])
    dl_steps = "".join(
        f'<li><span class="dot">{i}</span><p>{p}</p></li>' for i, p in enumerate(t["dl_steps"], 1)
    )
    main = f"""<section class="section band-white" id="descargar"><div class="wrap two-col">
<div class="stack"><div class="kicker">{t['dl_kicker']}</div><h2 class="section-title">{t['dl_h2']}</h2>
<div class="actions"><a class="btn btn-dark" href="{APK_URL}">{svg(ICONS['download'], 24, '#ffffff', 1.9)}{t['dl_btn']}</a></div></div>
<div class="stack" style="gap:24px"><ol class="placements" style="margin:0">{dl_steps}</ol><p class="muted">{t['dl_note']}</p></div>
</div></section>
<section class="section" id="como-funciona"><div class="wrap">
<div class="stack"><div class="kicker">{t['how_kicker']}</div><h2 class="section-title">{t['how_h2']}</h2></div>
<ol class="steps grid-3">{steps}</ol>
</div></section>
<section class="section" id="funciones" style="padding-top:0"><div class="wrap">
<h2 class="section-title">{t['features_h2']}</h2>
<div class="grid-3 features">{features}</div>
</div></section>
<section class="section band-white" id="estadisticas"><div class="wrap stats">
<div class="stack" style="gap:20px"><div class="kicker">{t['stats_kicker']}</div><h2 class="section-title">{t['stats_h2']}</h2>
<p class="muted" style="font-size:18px">{t['stats_p']}</p><ul class="stat-list">{stats_items}</ul>
<p class="muted" style="font-size:14px">{t['stats_example']}</p></div>
<div class="shots">{stats_shots}</div>
</div></section>
<section class="section"><div class="wrap">
<div class="split"><h2 class="section-title" style="max-width:640px">{t['looks_h2']}</h2><p class="muted" style="font-size:18px">{t['looks_p']}</p></div>
<div class="grid-3 looks">{looks}</div>
</div></section>
<section class="section"><div class="wrap privacy">
<div class="stack"><div class="kicker">{t['priv_kicker']}</div><h2 class="section-title">{t['priv_h2']}</h2>
<p class="muted" style="font-size:18px">{t['priv_p']}</p>
<a href="{rel(slug, SLUGS['privacy'][lang])}" style="font-weight:600">{t['priv_link']}</a></div>
<ul class="checks">{checks}</ul>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
<div class="cta"><div class="stack" style="gap:12px;max-width:760px"><div class="kicker">{t['biz_kicker']}</div><h2>{t['biz_h2']}</h2><p>{t['biz_p']}</p></div>
<a class="btn btn-light" href="{rel(slug, SLUGS['ads'][lang])}">{t['biz_btn']}</a></div>
</div></section>"""
    return layout(lang, "home", t["home_title"], t["home_desc"], hero, main)


def page_ads(lang):
    t = TEXTS[lang]
    hero = f"""<div class="hero-body single">
<div class="stack" style="gap:26px">
<div class="kicker">{t['ads_kicker']}</div>
<h1>{t['ads_h1']}</h1>
<p class="lead">{t['ads_lead']}</p>
<div class="actions"><a class="btn btn-light" href="{mailto(t['mail_subject'], t['mail_body'])}">{svg(ICONS['mail'], 22, '#2e3a73', 1.9)}{t['ads_btn']}</a></div>
</div></div>"""
    benefits = "".join(
        f'<div class="card benefit"><div class="icon-tile">{svg(ICONS[ic], 26, "#2e3a73", 1.8)}</div>'
        f'<div class="stack" style="gap:8px"><h3>{h}</h3><p class="muted">{p}</p></div></div>'
        for ic, h, p in t["benefits"]
    )
    places = "".join(
        f'<li><span class="dot">{i}</span><div><strong style="font-size:19px">{h}</strong><p class="muted">{p}</p></div></li>'
        for i, (h, p) in enumerate(t["placements"], 1)
    )
    needs = "".join(f"<li>{n}</li>" for n in t["needs"])
    main = f"""<section class="section"><div class="wrap">
<h2 class="section-title">{t['ads_why']}</h2>
<div class="grid-2" style="margin-top:48px">{benefits}</div>
</div></section>
<section class="section band-white"><div class="wrap two-col">
<div><h2 class="section-title">{t['ads_where']}</h2><ol class="placements">{places}</ol>
<p class="muted" style="margin-top:24px">{t['ads_where_note']}</p></div>
<div class="phone"><div class="phone-screen">
<div class="muted" style="font-size:13px;font-weight:600;padding:0 4px">{t['ad_caption']}</div>
<div class="ad"><div class="ad-img">{t['ad_image']}</div><div class="ad-body">
<span class="muted" style="font-size:11px">{t['ad_label']}</span><strong>{t['ad_title']}</strong>
<span class="muted">{t['ad_text']}</span><span class="ad-open">{t['ad_open']}</span></div></div>
</div></div>
</div></section>
<section class="section"><div class="wrap two-col">
<div class="stack" style="gap:24px"><h2 class="section-title" style="font-size:40px">{t['ads_need']}</h2><ul class="list">{needs}</ul></div>
<div class="card stack"><h2 style="font-size:32px">{t['ads_rates']}</h2><p class="muted" style="font-size:18px">{t['ads_rates_p']}</p>
<a href="{mailto(t['mail_rates_subject'])}" style="font-weight:600">{t['ads_rates_link']}</a></div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
<div class="cta"><div class="stack" style="gap:12px"><h2>{t['ads_talk']}</h2><p>{t['ads_talk_p']}</p></div>
<a class="btn btn-light" href="{mailto(t['mail_subject'], t['mail_body'])}">{EMAIL}</a></div>
</div></section>"""
    return layout(lang, "ads", t["ads_title"], t["ads_desc"], hero, main)


def page_privacy(lang):
    t = TEXTS[lang]
    hero = f"""<div class="hero-body single" style="padding-top:40px;padding-bottom:72px">
<div class="stack"><h1 style="font-size:clamp(40px,5vw,60px)">{t['privacy_h1']}</h1>
<p class="lead">{t['updated']}</p></div></div>"""
    mail = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
    sections, toc = [], []
    for anchor, heading, paras in t["legal"]:
        body = ""
        for p in paras:
            if isinstance(p, list):
                body += "<ul>" + "".join(f"<li>{x}</li>" for x in p) + "</ul>"
            else:
                body += "<p>" + p.format(mail=mail, domain=DOMAIN) + "</p>"
        sections.append(f'<section id="{anchor}"><h2>{heading}</h2>{body}</section>')
        toc.append(f'<a href="#{anchor}">{heading}</a>')
    main = f"""<section class="section" style="padding-top:64px"><div class="wrap legal">
<article><div class="summary">{t['summary']}</div>{''.join(sections)}</article>
<aside class="toc"><div class="kicker">{t['toc']}</div><nav aria-label="{t['toc']}" class="stack" style="gap:10px">{''.join(toc)}</nav></aside>
</div></section>"""
    return layout(lang, "privacy", t["privacy_title"], t["privacy_desc"], hero, main)


# ----------------------------------------------------------------- generación

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "src/style.css", OUT / "assets/style.css")
    shutil.copytree(ROOT / "src/fonts", OUT / "assets/fonts")
    shutil.copytree(ROOT / "src/img", OUT / "assets/img")
    for lang in LANGS:
        for page, fn in [("home", page_home), ("ads", page_ads), ("privacy", page_privacy)]:
            target = OUT / SLUGS[page][lang] / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(fn(lang), encoding="utf-8")
    # Catálogo de patrocinio que lee la app (SPONSORS_URL). Vacío hasta la primera campaña.
    catalog = {"enabled": False, "campaigns": []}
    if "--demo" in sys.argv:
        base = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--base=")), BASE_URL)
        demo = dict(DEMO_CAMPAIGN, imageUrl=f"{base.rstrip('/')}/assets/img/demo-anuncio.png")
        catalog = {"enabled": True, "campaigns": [demo]}
    (OUT / "sponsors.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    release = dict(
        RELEASE,
        url=f"https://github.com/martinezpenya/giracolchon-web/releases/download/v{RELEASE['version']}/giracolchon.apk",
    )
    (OUT / "version.json").write_text(
        json.dumps(release, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    # La 404 se sirve en cualquier ruta: sus enlaces relativos pasan a absolutos.
    import re
    page404 = re.sub(
        r'(href|src)="(?!https?:|mailto:|#|/)(?:\./)?([^"]*)"', r'\1="/\2"', page_home("es")
    )
    (OUT / "404.html").write_text(page404, encoding="utf-8")
    urls = "".join(
        f"<url><loc>{BASE_URL}/{SLUGS[p][l]}</loc></url>" for p in SLUGS for l in LANGS
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Generadas {len(LANGS) * 3} páginas en {OUT}")


if __name__ == "__main__":
    main()
