"""Textos de interface e páginas institucionais em inglês e espanhol.
O português é o idioma principal e fica no próprio gerar.py. As chaves de UI são o texto em português."""

IDIOMAS_REAIS = ["pt", "en", "es", "fr", "de", "it", "ja", "zh", "ar"]
HTML_LANG = {"pt": "pt-BR", "en": "en", "es": "es", "fr": "fr", "de": "de", "it": "it", "ja": "ja", "zh": "zh-CN", "ar": "ar"}
OG_LOCALE = {"pt": "pt_BR", "en": "en_US", "es": "es_ES", "fr": "fr_FR", "de": "de_DE", "it": "it_IT", "ja": "ja_JP", "zh": "zh_CN", "ar": "ar_AR"}
SIGLA = {"pt": "PT", "en": "EN", "es": "ES", "fr": "FR", "de": "DE", "it": "IT", "ja": "JA", "zh": "ZH", "ar": "AR"}

MESES = {
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}
DIAS = {
    "pt": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "es": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
}

EDITORIAS = {
    "en": {
        "games": ("Games", "Releases, gaming culture and the studios behind the games."),
        "cinema": ("Movies & TV", "Premieres, behind the scenes and everything around the screening."),
        "tecnologia": ("Technology", "Tools, digital security and everyday tech without the jargon."),
        "anime": ("Anime", "Anime, manga and otaku culture: seasonal premieres, adaptations and what's trending."),
        "curiosidades": ("Curiosities", "Questions everyone has asked, answered with science."),
    },
    "es": {
        "games": ("Juegos", "Lanzamientos, cultura gamer y los estudios detrás de los juegos."),
        "cinema": ("Cine y series", "Estrenos, entre bastidores y todo lo que pasa antes y después de la función."),
        "tecnologia": ("Tecnología", "Herramientas, seguridad digital y la tecnología de todos los días, sin jerga."),
        "anime": ("Anime", "Anime, manga y cultura otaku: estrenos de la temporada, adaptaciones y lo que está en tendencia."),
        "curiosidades": ("Curiosidades", "Preguntas que todos nos hicimos, respondidas con ciencia."),
    },
}

# Cada chave é o texto original em português.
UI = {
    "en": {
        "Pular para o conteúdo": "Skip to content",
        "Início": "Home",
        "Buscar": "Search",
        "Alternar tema": "Toggle theme",
        "Abrir menu": "Open menu",
        "Editorias": "Sections",
        "Idioma / Language": "Language",
        "Traduzir esta página / Translate": "Language / Idioma",
        "Traduzir / Translate": "Language / Idioma",
        "Traduzir / Translate:": "Language / Idioma:",
        "página inicial": "home page",
        "Cinema, games e tecnologia explicados com calma, de olho no que importa.": "Movies, games and tech explained calmly, with an eye on what matters.",
        "Institucional": "About the site",
        "Sobre nós": "About us",
        "Contato e anúncios": "Contact and advertising",
        "Equipe Aloha": "Aloha Team",
        "Política editorial": "Editorial policy",
        "Termos de uso": "Terms of use",
        "Privacidade": "Privacy",
        "RSS": "RSS (Portuguese)",
        "Ilustração": "Illustration",
        "min de leitura": "min read",
        "min": "min",
        "Mais lidas": "Most read",
        "Voltar às notícias anteriores de": "Back to earlier stories in",
        "Ver mais notícias de": "More stories in",
        "Ver tudo em": "See all in",
        "Mais em": "More in",
        "Ainda não publicamos matérias nesta editoria. Volte em breve.": "We have not published anything in this section yet. Check back soon.",
        "Você está em": "You are here",
        "Por": "By",
        "Compartilhe": "Share",
        "Copiar link": "Copy link",
        "Leia também": "Read next",
        "Atualizado em": "Updated",
        "Atualização:": "Update:",
        "Compartilhar no": "Share on",
        "Assuntos": "Topics",
        "matéria": "article",
        "matérias": "articles",
        "sobre este assunto.": "on this topic.",
        "Matérias da ALOHA NOTÍCIAS sobre": "ALOHA NOTÍCIAS articles about",
        "Busque matérias da ALOHA NOTÍCIAS.": "Search ALOHA NOTÍCIAS articles.",
        "Buscar matérias": "Search articles",
        "Ex.: GTA 6, Vingadores, Switch 2": "E.g. GTA 6, Avengers, Switch 2",
        "Página não encontrada": "Page not found",
        "Essa onda passou": "That wave has passed",
        "A página que você procurou não existe ou mudou de endereço.": "The page you were looking for does not exist or has moved.",
        "Voltar para a página inicial": "Back to the home page",
        "ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia": "ALOHA NOTÍCIAS: news, movies, games and technology",
        "Notícias, cinema, games e tecnologia, explicados com calma.": "News, movies, games and technology, explained calmly.",
        "Destaques": "Top stories",
        "Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.": "Type a topic, for example: GTA 6, Marvel or movies.",
        "Nada encontrado para": "Nothing found for",
        "Tente outra palavra.": "Try another word.",
        "matéria encontrada": "article found",
        "matérias encontradas": "articles found",
        "Link copiado": "Link copied",
        "Copie o endereço na barra do navegador": "Copy the address from your browser bar",
        "Aviso de cookies": "Cookie notice",
        "Aceitar": "Accept",
        "Recusar": "Decline",
        "Leia esta página em português (idioma original)": "Read this page in Portuguese (original language)",
        "Esta matéria foi escrita em português e adaptada para o inglês pela equipe.": "This article was written in Portuguese and adapted into English by our team.",
        "Esta página também existe em": "This page is also available in",
        "Original em português": "Original in Portuguese",
    },
    "es": {
        "Pular para o conteúdo": "Saltar al contenido",
        "Início": "Inicio",
        "Buscar": "Buscar",
        "Alternar tema": "Cambiar tema",
        "Abrir menu": "Abrir menú",
        "Editorias": "Secciones",
        "Idioma / Language": "Idioma",
        "Traduzir esta página / Translate": "Idioma / Language",
        "Traduzir / Translate": "Idioma / Language",
        "Traduzir / Translate:": "Idioma / Language:",
        "página inicial": "página de inicio",
        "Cinema, games e tecnologia explicados com calma, de olho no que importa.": "Cine, juegos y tecnología explicados con calma, atentos a lo que importa.",
        "Institucional": "Sobre el sitio",
        "Sobre nós": "Quiénes somos",
        "Contato e anúncios": "Contacto y publicidad",
        "Equipe Aloha": "Equipo Aloha",
        "Política editorial": "Política editorial",
        "Termos de uso": "Términos de uso",
        "Privacidade": "Privacidad",
        "RSS": "RSS (portugués)",
        "Ilustração": "Ilustración",
        "min de leitura": "min de lectura",
        "min": "min",
        "Mais lidas": "Lo más leído",
        "Voltar às notícias anteriores de": "Volver a las noticias anteriores de",
        "Ver mais notícias de": "Ver más noticias de",
        "Ver tudo em": "Ver todo en",
        "Mais em": "Más en",
        "Ainda não publicamos matérias nesta editoria. Volte em breve.": "Todavía no hemos publicado nada en esta sección. Vuelve pronto.",
        "Você está em": "Estás en",
        "Por": "Por",
        "Compartilhe": "Comparte",
        "Copiar link": "Copiar enlace",
        "Leia também": "Sigue leyendo",
        "Atualizado em": "Actualizado",
        "Atualização:": "Actualización:",
        "Compartilhar no": "Compartir en",
        "Assuntos": "Temas",
        "matéria": "artículo",
        "matérias": "artículos",
        "sobre este assunto.": "sobre este tema.",
        "Matérias da ALOHA NOTÍCIAS sobre": "Artículos de ALOHA NOTÍCIAS sobre",
        "Busque matérias da ALOHA NOTÍCIAS.": "Busca artículos de ALOHA NOTÍCIAS.",
        "Buscar matérias": "Buscar artículos",
        "Ex.: GTA 6, Vingadores, Switch 2": "Ej.: GTA 6, Avengers, Switch 2",
        "Página não encontrada": "Página no encontrada",
        "Essa onda passou": "Esa ola ya pasó",
        "A página que você procurou não existe ou mudou de endereço.": "La página que buscabas no existe o cambió de dirección.",
        "Voltar para a página inicial": "Volver al inicio",
        "ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia": "ALOHA NOTÍCIAS: noticias, cine, juegos y tecnología",
        "Notícias, cinema, games e tecnologia, explicados com calma.": "Noticias, cine, juegos y tecnología, explicados con calma.",
        "Destaques": "Destacados",
        "Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.": "Escribe un tema, por ejemplo: GTA 6, Marvel o cine.",
        "Nada encontrado para": "No se encontró nada para",
        "Tente outra palavra.": "Prueba con otra palabra.",
        "matéria encontrada": "artículo encontrado",
        "matérias encontradas": "artículos encontrados",
        "Link copiado": "Enlace copiado",
        "Copie o endereço na barra do navegador": "Copia la dirección de la barra del navegador",
        "Aviso de cookies": "Aviso de cookies",
        "Aceitar": "Aceptar",
        "Recusar": "Rechazar",
        "Leia esta página em português (idioma original)": "Lee esta página en portugués (idioma original)",
        "Esta matéria foi escrita em português e adaptada para o inglês pela equipe.": "Este artículo fue escrito en portugués y adaptado al español por el equipo.",
        "Esta página também existe em": "Esta página también está disponible en",
        "Original em português": "Original en portugués",
    },
}

NOMES_IDIOMA = {"pt": "Português", "en": "English", "es": "Español"}

# Páginas institucionais (título, descrição, HTML do corpo)
PAGINAS = {"en": {}, "es": {}}

PAGINAS["en"]["sobre.html"] = ("About us", "Who is behind ALOHA NOTÍCIAS.", """
<p>ALOHA NOTÍCIAS is a Brazilian news site for people who want to understand what is going on without the noise. Our focus is movies, games and technology: premieres, releases and what is trending, with the facts checked.</p>
<p>We write in Portuguese first. This English edition is adapted by our team for readers outside Brazil, so you will see Brazilian dates and release details explained where they matter.</p>
<h2>How we work</h2>
<p>Every article cites its sources, separates fact from opinion and is openly corrected when we get something wrong. The details are in our <a href="politica-editorial.html">editorial policy</a>.</p>
<h2>The name</h2>
<p><em>Aloha</em> is the Hawaiian greeting that also means affection and respect. That is how we want to treat the people who read us.</p>
<h2>Get in touch</h2>
<p>Suggestions, corrections and partnerships go through the <a href="contato.html">contact page</a>.</p>""")

PAGINAS["es"]["sobre.html"] = ("Quiénes somos", "Quién está detrás de ALOHA NOTÍCIAS.", """
<p>ALOHA NOTÍCIAS es un sitio de noticias de Brasil para quienes quieren entender lo que pasa sin ruido. Nos centramos en cine, juegos y tecnología: estrenos, lanzamientos y lo que está en tendencia, con los datos verificados.</p>
<p>Escribimos primero en portugués. Esta edición en español la adapta nuestro equipo para lectores de fuera de Brasil, y por eso explicamos las fechas y los detalles de estreno brasileños cuando importan.</p>
<h2>Cómo trabajamos</h2>
<p>Cada artículo cita sus fuentes, separa los hechos de la opinión y se corrige a la vista de todos cuando nos equivocamos. Los detalles están en nuestra <a href="politica-editorial.html">política editorial</a>.</p>
<h2>El nombre</h2>
<p><em>Aloha</em> es el saludo hawaiano que también significa cariño y respeto. Así queremos tratar a quienes nos leen.</p>
<h2>Contacto</h2>
<p>Sugerencias, correcciones y alianzas, en la <a href="contato.html">página de contacto</a>.</p>""")

PAGINAS["en"]["politica-editorial.html"] = ("Editorial and corrections policy", "How ALOHA NOTÍCIAS researches, writes, illustrates and corrects its articles.", """
<p>This page explains, in plain language, how ALOHA NOTÍCIAS content is made. If we fail to follow any of it, we want to know.</p>
<h2>How we check facts</h2>
<p>We try to confirm every important piece of information in more than one source before publishing. Dates, prices and numbers only go into the text when they appear in the sources we consulted, which we list at the end of each article. When something comes from a single source, or is not confirmed yet, we say so in the text.</p>
<h2>How we choose topics</h2>
<p>We prioritize what is trending and useful to readers: premieres, releases, dates and news from movies, games and technology. We do not publish just to repeat a press release. In each article we try to gather what is confirmed, organize what is still unknown and show where each piece of information came from.</p>
<h2>Rumors and leaks</h2>
<p>Rumors, leaks and behind-the-scenes information only appear when they are relevant, always labeled as unconfirmed and with the source named. We do not treat a rumor as fact.</p>
<h2>Review before publishing</h2>
<p>No article goes live without review and approval from a person on the team.</p>
<h2>Images and videos</h2>
<p>Our covers are put together by our team from free-to-use stock photos, such as Unsplash, with the photographer credited in the article, plus graphic elements of our own. We do not use posters, covers or protected images from movies, games or characters. The video in an article, when there is one, is official content embedded from the channel where it was published, with the channel named. If you are the author or owner of an image and want a different credit or its removal, write to us.</p>
<h2>Corrections</h2>
<p>When we find a mistake, we fix the article and mark the correction in the text. We also update articles when dates or facts change, so the content does not go stale. If you found an error, send the article and what is wrong through the <a href="contato.html">contact page</a>. We reply as soon as we can.</p>
<h2>Independence</h2>
<p>Our editorial content is independent. Ads, when they exist, are kept apart from the text and do not influence what we publish. If an article involves sponsorship or a partnership, we will say so clearly.</p>
<h2>Translations</h2>
<p>Portuguese is our original language. The English and Spanish editions are adapted by our team, not translated word for word, and may leave out details that only matter to a Brazilian audience. If the two versions differ, the Portuguese original prevails.</p>""")

PAGINAS["es"]["politica-editorial.html"] = ("Política editorial y de correcciones", "Cómo ALOHA NOTÍCIAS investiga, escribe, ilustra y corrige sus artículos.", """
<p>Esta página explica, en lenguaje sencillo, cómo se hace el contenido de ALOHA NOTÍCIAS. Si algo de esto no se cumple, queremos saberlo.</p>
<h2>Cómo verificamos</h2>
<p>Intentamos confirmar cada dato importante en más de una fuente antes de publicar. Las fechas, los precios y las cifras solo entran en el texto cuando aparecen en las fuentes consultadas, que listamos al final de cada artículo. Cuando algo viene de una sola fuente o aún no está confirmado, lo decimos en el texto.</p>
<h2>Cómo elegimos los temas</h2>
<p>Priorizamos lo que está en tendencia y le sirve al lector: estrenos, lanzamientos, fechas y novedades de cine, juegos y tecnología. No publicamos solo para repetir un comunicado. En cada artículo intentamos reunir lo confirmado, ordenar lo que aún no se sabe e indicar de dónde viene cada dato.</p>
<h2>Rumores y filtraciones</h2>
<p>Los rumores, las filtraciones y la información de bastidores solo aparecen cuando son relevantes, siempre señalados como no confirmados y con la fuente indicada. No tratamos un rumor como un hecho.</p>
<h2>Revisión antes de publicar</h2>
<p>Ningún artículo sale al aire sin la revisión y la aprobación de una persona del equipo.</p>
<h2>Imágenes y videos</h2>
<p>Nuestras portadas las arma el equipo con fotos de bancos de imágenes de uso libre, como Unsplash, con el crédito del autor en el artículo, y con elementos gráficos propios. No usamos pósteres, portadas ni imágenes protegidas de películas, juegos o personajes. El video de un artículo, cuando lo hay, es contenido oficial incrustado desde el canal donde se publicó, con el nombre del canal. Si eres autor o dueño de una imagen y quieres otro crédito o su retiro, escríbenos.</p>
<h2>Correcciones</h2>
<p>Cuando encontramos un error, corregimos el artículo y marcamos la corrección en el texto. También actualizamos artículos cuando cambian fechas o datos, para que el contenido no quede desactualizado. Si encontraste un error, envía el artículo y lo que está mal por la <a href="contato.html">página de contacto</a>. Respondemos lo antes posible.</p>
<h2>Independencia</h2>
<p>El contenido editorial es independiente. Los anuncios, cuando existan, van separados del texto y no influyen en lo que publicamos. Si un artículo tiene patrocinio o una alianza, lo diremos con claridad.</p>
<h2>Traducciones</h2>
<p>El portugués es nuestro idioma original. Las ediciones en inglés y en español las adapta nuestro equipo, no se traducen palabra por palabra, y pueden omitir detalles que solo importan al público brasileño. Si las versiones difieren, prevalece el original en portugués.</p>""")

PAGINAS["en"]["equipe.html"] = ("Aloha Team", "Who signs the ALOHA NOTÍCIAS articles and what we cover.", """
<p>Aloha Team is the byline of the ALOHA NOTÍCIAS newsroom. It brings together the people who research, write, build the covers and review what is published here.</p>
<h2>Who is behind it</h2>
<p>ALOHA NOTÍCIAS is an independent editorial project, run by a team and with no ties to studios, producers or manufacturers. Every article is reviewed and approved by a person before it goes live.</p>
<h2>What to expect</h2>
<p>Information checked in more than one source, sources cited at the end of every piece, rumors labeled as such and corrections made in the open. If something is wrong, we want to know.</p>
<h2>What we cover</h2>
<ul>@@EDITORIAS@@</ul>
<h2>How we work</h2>
<p>We confirm facts in more than one source, cite our sources at the end of each article and correct errors openly. See the <a href="politica-editorial.html">editorial policy</a>.</p>
<h2>Get in touch</h2>
<p>Story tips, corrections and partnerships: <a href="contato.html">contact page</a>.</p>""")

PAGINAS["es"]["equipe.html"] = ("Equipo Aloha", "Quién firma los artículos de ALOHA NOTÍCIAS y qué cubrimos.", """
<p>Equipo Aloha es la firma de la redacción de ALOHA NOTÍCIAS. Reúne a quienes investigan, escriben, arman las portadas y revisan lo que se publica aquí.</p>
<h2>Quién está detrás</h2>
<p>ALOHA NOTÍCIAS es un proyecto editorial independiente, dirigido por un equipo y sin vínculos con estudios, productoras ni fabricantes. Cada artículo lo revisa y aprueba una persona antes de salir al aire.</p>
<h2>Qué puedes esperar</h2>
<p>Información verificada en más de una fuente, fuentes citadas al final de cada texto, rumores señalados como tales y correcciones hechas a la vista. Si algo está mal, queremos saberlo.</p>
<h2>Qué cubrimos</h2>
<ul>@@EDITORIAS@@</ul>
<h2>Cómo trabajamos</h2>
<p>Confirmamos los datos en más de una fuente, citamos las fuentes al final de cada artículo y corregimos los errores abiertamente. Consulta la <a href="politica-editorial.html">política editorial</a>.</p>
<h2>Contacto</h2>
<p>Pistas, correcciones y alianzas: <a href="contato.html">página de contacto</a>.</p>""")

PAGINAS["en"]["contato.html"] = ("Contact and advertising", "Get in touch with the ALOHA NOTÍCIAS newsroom.", """
<p>Email us at <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. To speed things up, put the reason in the subject line. We read English, Spanish and Portuguese.</p>
<h2>Story tips</h2><p>Saw something worth an article? Send the topic and, if you have it, a link to the source.</p>
<h2>Corrections</h2><p>Found a mistake? Send the article address and what is wrong, with a source if possible. See how we handle corrections in the <a href="politica-editorial.html">editorial policy</a>.</p>
<h2>Copyright and images</h2><p>If you are the author or owner of an image, text or video and want to fix the credit or ask for removal, write to us with the page address and proof of ownership.</p>
<h2>Advertising and partnerships</h2><p>To advertise or propose a partnership, write to the same address. Sponsored content will always be labeled as such.</p>
<h2>Privacy</h2><p>Requests about personal data follow what is in the <a href="privacidade.html">privacy policy</a>.</p>""")

PAGINAS["es"]["contato.html"] = ("Contacto y publicidad", "Habla con la redacción de ALOHA NOTÍCIAS.", """
<p>Escríbenos a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Para agilizar, pon el motivo en el asunto. Leemos español, inglés y portugués.</p>
<h2>Sugerencias de temas</h2><p>¿Viste algo que merece un artículo? Envía el tema y, si lo tienes, el enlace de la fuente.</p>
<h2>Correcciones</h2><p>¿Encontraste un error? Envía la dirección del artículo y qué está mal, con la fuente si es posible. Mira cómo tratamos las correcciones en la <a href="politica-editorial.html">política editorial</a>.</p>
<h2>Derechos de autor e imágenes</h2><p>Si eres autor o dueño de una imagen, texto o video y quieres corregir el crédito o pedir su retiro, escríbenos con la dirección de la página y la prueba de autoría.</p>
<h2>Publicidad y alianzas</h2><p>Para anunciar o proponer una alianza, escribe al mismo correo. El contenido patrocinado siempre se identificará como tal.</p>
<h2>Privacidad</h2><p>Las solicitudes sobre datos personales siguen lo que dice la <a href="privacidade.html">política de privacidad</a>.</p>""")

PAGINAS["en"]["termos.html"] = ("Terms of use", "Terms of use of the ALOHA NOTÍCIAS site.", """
<p>Last updated: November 2026. By using ALOHA NOTÍCIAS (alohanoticias.com) you agree to these terms. If you do not agree, please do not use the site.</p>
<h2>What the site is</h2>
<p>ALOHA NOTÍCIAS publishes articles about movies, games, technology, news and curiosities. The content is offered for information and entertainment.</p>
<h2>Information, not advice</h2>
<p>Articles are informational and do not replace the guidance of a professional. We do our best to publish correct and current information, but data, prices and dates may change after publication.</p>
<h2>Intellectual property</h2>
<p>The original text and illustrations on the site belong to ALOHA NOTÍCIAS. You may share links and quote short excerpts with credit and a link to the original article. You may not copy whole articles, republish them or use them to train automated systems without written permission.</p>
<p>Third-party brands, names, images and videos mentioned in articles belong to their owners and appear for informational purposes, with credit. If you own content and want to fix the credit or request removal, contact us through the <a href="contato.html">contact page</a>.</p>
<h2>Links and third-party services</h2>
<p>The site may link to other sites and embed content from services such as YouTube. We do not control those addresses and are not responsible for what they publish or for their rules.</p>
<h2>Advertising</h2>
<p>The site may show ads. When it does, they will be identified as advertising and kept apart from editorial content. An ad does not mean we endorse the advertised product or service.</p>
<h2>Acceptable use</h2>
<p>You agree not to try to harm the operation of the site, access restricted areas, send malicious code or use the site for unlawful purposes.</p>
<h2>Limitation of liability</h2>
<p>The site is provided as is. We do not guarantee that it will always be available or error free, and we are not responsible for losses resulting from the use of the information published, to the extent the law allows.</p>
<h2>Privacy</h2>
<p>Data handling is described in the <a href="privacidade.html">privacy policy</a>.</p>
<h2>Changes and governing law</h2>
<p>We may change these terms, and the version in force is the one published on this page, with its update date. These terms are governed by the laws of Brazil. The Portuguese version prevails if there is any difference.</p>
<h2>Contact</h2>
<p>Questions about these terms: <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>""")

PAGINAS["es"]["termos.html"] = ("Términos de uso", "Términos de uso del sitio ALOHA NOTÍCIAS.", """
<p>Última actualización: noviembre de 2026. Al usar ALOHA NOTÍCIAS (alohanoticias.com) aceptas estos términos. Si no estás de acuerdo, te pedimos que no uses el sitio.</p>
<h2>Qué es el sitio</h2>
<p>ALOHA NOTÍCIAS publica artículos sobre cine, juegos, tecnología, noticias y curiosidades. El contenido se ofrece con fines informativos y de entretenimiento.</p>
<h2>Información, no asesoría</h2>
<p>Los artículos son informativos y no sustituyen la orientación de un profesional. Hacemos lo posible por publicar información correcta y actual, pero los datos, precios y fechas pueden cambiar después de la publicación.</p>
<h2>Propiedad intelectual</h2>
<p>Los textos e ilustraciones originales del sitio pertenecen a ALOHA NOTÍCIAS. Puedes compartir enlaces y citar fragmentos breves, con crédito y enlace al artículo original. No está permitido copiar artículos completos, republicarlos ni usarlos para entrenar sistemas automáticos sin autorización por escrito.</p>
<p>Las marcas, nombres, imágenes y videos de terceros citados en los artículos pertenecen a sus dueños y aparecen con fines informativos y con crédito. Si eres dueño de un contenido y quieres corregir el crédito o pedir su retiro, contáctanos por la <a href="contato.html">página de contacto</a>.</p>
<h2>Enlaces y servicios de terceros</h2>
<p>El sitio puede tener enlaces a otros sitios e incrustar contenido de servicios como YouTube. No controlamos esas direcciones y no nos hacemos responsables de lo que publican ni de sus reglas.</p>
<h2>Publicidad</h2>
<p>El sitio podrá mostrar anuncios. Cuando los haya, se identificarán como publicidad y se mantendrán separados del contenido editorial. Que haya un anuncio no significa que respaldemos el producto o servicio anunciado.</p>
<h2>Uso adecuado</h2>
<p>Aceptas no intentar perjudicar el funcionamiento del sitio, acceder a áreas restringidas, enviar código malicioso ni usar el sitio con fines ilegales.</p>
<h2>Limitación de responsabilidad</h2>
<p>El sitio se ofrece tal cual. No garantizamos que esté siempre disponible ni libre de errores, y no nos hacemos responsables de pérdidas derivadas del uso de la información publicada, dentro de lo que permita la ley.</p>
<h2>Privacidad</h2>
<p>El tratamiento de datos se describe en la <a href="privacidade.html">política de privacidad</a>.</p>
<h2>Cambios y ley aplicable</h2>
<p>Podemos cambiar estos términos, y la versión vigente es la publicada en esta página, con su fecha de actualización. Estos términos se rigen por las leyes de Brasil. Si hay diferencias, prevalece la versión en portugués.</p>
<h2>Contacto</h2>
<p>Dudas sobre estos términos: <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>""")

PAGINAS["en"]["privacidade.html"] = ("Privacy", "Privacy policy of ALOHA NOTÍCIAS.", """
<p>Last updated: November 2026. We follow Brazil's General Data Protection Law (LGPD, Law 13,709/2018). Here is, plainly, what happens to your data when you visit this site.</p>
<h2>What we collect</h2>
<p>We do not ask you to sign up and we do not use advertising or tracking cookies. We only store, in your own browser, your light or dark theme preference.</p>
<p>We count visits with a statistics service that does not use cookies and does not identify you personally (Cloudflare Web Analytics). What we see is aggregated, such as most-read pages, country and device type.</p>
<h2>Third-party services</h2>
<p>Fonts come from Google Fonts. Photos may come from Unsplash, and videos are embedded from YouTube in enhanced privacy mode (youtube-nocookie.com). When these items load, those services receive your IP address and may have their own privacy rules. The site is hosted by Cloudflare.</p>
@@ANUNCIOS@@<h2>Contact email</h2>
<p>If you write to us, we use your email only to reply. We do not sell or share your data.</p>
<h2>Your rights</h2>
<p>You can ask for information about the data we hold about you, and for its correction or deletion, by writing through the <a href="contato.html">contact page</a>.</p>
<h2>Changes</h2>
<p>If this policy changes, the date above will be updated. If we start using cookies, ads or a newsletter, we will say so here first. The Portuguese version prevails if there is any difference.</p>""")

PAGINAS["es"]["privacidade.html"] = ("Privacidad", "Política de privacidad de ALOHA NOTÍCIAS.", """
<p>Última actualización: noviembre de 2026. Cumplimos la Ley General de Protección de Datos de Brasil (LGPD, Ley 13.709/2018). Aquí está, de forma directa, lo que pasa con tus datos cuando visitas este sitio.</p>
<h2>Qué recopilamos</h2>
<p>No pedimos registro y no usamos cookies de publicidad ni de rastreo. Solo guardamos, en tu propio navegador, tu preferencia de tema claro u oscuro.</p>
<p>Medimos las visitas con un servicio de estadísticas que no usa cookies y no te identifica personalmente (Cloudflare Web Analytics). Lo que vemos es agregado, como las páginas más leídas, el país y el tipo de dispositivo.</p>
<h2>Servicios de terceros</h2>
<p>Las fuentes tipográficas vienen de Google Fonts. Las fotos pueden venir de Unsplash y los videos se incrustan desde YouTube en modo de privacidad mejorada (youtube-nocookie.com). Al cargar esos contenidos, esos servicios reciben tu dirección IP y pueden tener sus propias reglas de privacidad. El sitio está alojado en Cloudflare.</p>
@@ANUNCIOS@@<h2>Correo de contacto</h2>
<p>Si nos escribes, usaremos tu correo solo para responder. No vendemos ni compartimos tus datos.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir información sobre los datos que tenemos de ti, su corrección o eliminación, escribiendo por la <a href="contato.html">página de contacto</a>.</p>
<h2>Cambios</h2>
<p>Si esta política cambia, se actualizará la fecha de arriba. Si empezamos a usar cookies, anuncios o un boletín, lo avisaremos aquí antes. Si hay diferencias, prevalece la versión en portugués.</p>""")

PRIV_ANUNCIOS = {
    "en": """<h2>Ads and cookies</h2>
<p>This site shows Google AdSense ads. With your permission, Google and its partners may use cookies and device identifiers to show ads and measure their performance. Ads only load after you click &ldquo;Accept&rdquo; on the cookie notice; if you decline, the site keeps working normally, without ads. You can change your mind at any time in <a href="#" id="reabrir-consent">cookie preferences</a>.</p>
<p>Learn how Google uses data from partner sites at <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. You can also manage personalized ads at <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.</p>
""",
    "es": """<h2>Anuncios y cookies</h2>
<p>Este sitio muestra anuncios de Google AdSense. Con tu permiso, Google y sus socios pueden usar cookies e identificadores del dispositivo para mostrar anuncios y medir su rendimiento. Los anuncios solo se cargan después de que pulses &ldquo;Aceptar&rdquo; en el aviso de cookies; si rechazas, el sitio sigue funcionando con normalidad, sin anuncios. Puedes cambiar de opinión en cualquier momento en <a href="#" id="reabrir-consent">preferencias de cookies</a>.</p>
<p>Conoce cómo Google usa los datos de sitios asociados en <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. También puedes gestionar los anuncios personalizados en <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.</p>
""",
}


# ---------------------------------------------------------------- demais idiomas (um módulo por idioma)
CONSENT = {
    "en": "We use cookies to show ads and keep the site free. It is your choice: if you do not accept, we do not load ads.",
    "es": "Usamos cookies para mostrar anuncios y mantener el sitio gratuito. Tú eliges: si no aceptas, no cargamos anuncios.",
}
SABER = {"en": "Learn more", "es": "Más información"}

import importlib as _il
for _l in IDIOMAS_REAIS[3:]:
    try:
        _m = _il.import_module(f"i18n_{_l}")
    except ModuleNotFoundError:
        continue
    MESES[_l], DIAS[_l], EDITORIAS[_l], UI[_l], PAGINAS[_l] = _m.MES, _m.DIA, _m.ED, _m.UI, _m.PAG
    PRIV_ANUNCIOS[_l], CONSENT[_l], SABER[_l], NOMES_IDIOMA[_l] = _m.PRIV, _m.CONSENT, _m.SABER, _m.NOME
IDIOMAS_REAIS = [l for l in IDIOMAS_REAIS if l in ("pt", "en", "es") or l in UI]

# Textos de interface que faltavam em todos os idiomas (botões, busca, menu, barra lateral).
_K = ["Leia mais", "Pesquisar", "Mais recentes", "Matérias recentes", "Categorias", "Barra lateral", "Menu"]
_EXTRA = {
    "en": ["Read more", "Search", "Latest", "Recent articles", "Categories", "Sidebar", "Menu"],
    "es": ["Leer más", "Buscar", "Más recientes", "Artículos recientes", "Categorías", "Barra lateral", "Menú"],
    "fr": ["Lire la suite", "Rechercher", "Les plus récents", "Articles récents", "Catégories", "Barre latérale", "Menu"],
    "de": ["Weiterlesen", "Suchen", "Neueste", "Neueste Beiträge", "Kategorien", "Seitenleiste", "Menü"],
    "it": ["Leggi di più", "Cerca", "Più recenti", "Articoli recenti", "Categorie", "Barra laterale", "Menu"],
    "ja": ["続きを読む", "検索", "最新", "最新記事", "カテゴリー", "サイドバー", "メニュー"],
    "zh": ["阅读更多", "搜索", "最新", "最新文章", "分类", "侧边栏", "菜单"],
    "ar": ["اقرأ المزيد", "بحث", "الأحدث", "أحدث المقالات", "الأقسام", "الشريط الجانبي", "القائمة"],
}
for _l, _v in _EXTRA.items():
    for _k, _t in zip(_K, _v):
        UI[_l].setdefault(_k, _t)

_H1 = {"en": "news, movies, games, technology and curiosities", "es": "noticias, cine, juegos, tecnología y curiosidades", "fr": "actualités, cinéma, jeux, technologie et curiosités", "de": "Nachrichten, Kino, Spiele, Technik und Kurioses", "it": "notizie, cinema, giochi, tecnologia e curiosità", "ja": "ニュース、映画、ゲーム、テクノロジー、トリビア", "zh": "新闻、影视、游戏、科技与趣闻", "ar": "أخبار وسينما وألعاب وتقنية ومعلومات طريفة"}
for _l, _t in _H1.items():
    UI[_l].setdefault("notícias, cinema, games, tecnologia e curiosidades", _t)
