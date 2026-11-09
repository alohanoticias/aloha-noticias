"""Política de privacidade nos 9 idiomas do site.

Cada texto descreve o que o site realmente faz hoje (Google Analytics com regra por região, Cloudflare,
notificações OneSignal, conteúdo incorporado). Marcadores trocados pelo gerar.py:
  @@ANUNCIOS@@  -> seção de anúncios (só quando ANUNCIOS_ATIVOS = True)
  @@SEMADS@@    -> frase "não usamos cookies de publicidade" (só enquanto os anúncios estão desligados)
  @@MUDANCA@@   -> aviso de que a política será atualizada antes dos anúncios (só enquanto estão desligados)
Ao mudar algo no funcionamento do site (novo serviço, anúncios, newsletter), atualize todos os idiomas e a data.
"""

PRIV = {}
ANUNCIOS = {}
SEMADS = {}
MUDANCA = {}

# ------------------------------------------------------------------ português (versão de referência)
PRIV["pt"] = ("Política de privacidade", "Como a ALOHA NOTÍCIAS trata os dados de quem visita o site.", """
<p>Última atualização: 9 de novembro de 2026. Esta página explica, sem juridiquês, quais dados são tratados quando você visita o ALOHA NOTÍCIAS (alohanoticias.com), para quê e como você controla isso. Seguimos a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018).</p>
<h2>Quem é o responsável</h2>
<p>O responsável pelo tratamento dos dados descritos aqui é o ALOHA NOTÍCIAS. Para qualquer assunto de privacidade, escreva para <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>O que não coletamos</h2>
<p>O site não tem cadastro, login de leitor nem formulário que peça seus dados. Não sabemos o seu nome nem o seu e-mail, a menos que você nos escreva.@@SEMADS@@</p>
<h2>Estatísticas de visita (Google Analytics)</h2>
<p>Usamos o Google Analytics 4 para saber quantas pessoas leem cada página, de que tipo de aparelho e de que país ou cidade aproximada, e de onde a visita chegou (uma busca, uma rede social, o nosso canal no Telegram ou o link de um parceiro, que identificamos por etiquetas no endereço). O Google Analytics usa cookies e identificadores do navegador. Recebemos números agregados e não usamos esses dados para identificar você.</p>
<p>Na União Europeia, no Espaço Econômico Europeu, no Reino Unido e na Suíça, a medição só começa depois que você clica em &ldquo;Aceitar&rdquo; no aviso de cookies. Nos demais países, incluindo o Brasil, ela começa quando a página abre, com base no nosso interesse legítimo em entender como o site é usado. Em qualquer lugar você pode desligá-la clicando em &ldquo;Recusar&rdquo; no aviso ou em &ldquo;Preferências de cookies&rdquo;, no rodapé. Os dados ficam guardados pelo prazo de retenção configurado no Google Analytics. Saiba mais em <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">como o Google usa dados de sites parceiros</a>.</p>
<h2>Hospedagem e segurança (Cloudflare)</h2>
<p>O site é hospedado pela Cloudflare. Para entregar as páginas e proteger o site contra ataques, a Cloudflare processa dados técnicos de cada acesso, como endereço de IP, navegador e página pedida, e pode contar visitas de forma agregada, sem cookies.</p>
<h2>O que fica guardado no seu navegador</h2>
<p>Guardamos no próprio navegador (armazenamento local, não enviado para nós) a sua escolha de tema claro ou escuro, a sua resposta ao aviso de cookies e quais avisos do sino de novidades você já viu. Você pode apagar tudo isso limpando os dados do site no navegador.</p>
<h2>Notificações</h2>
<p>Se você ativar os avisos de novas matérias, o serviço OneSignal guarda um identificador do seu navegador para enviar as notificações. Nada é ativado sem o seu clique, e você pode desligar a qualquer momento nas configurações do navegador ou do celular.</p>
<h2>Conteúdo de outros sites</h2>
<p>As fontes de letra vêm do Google Fonts. Algumas fotos são exibidas a partir do endereço de origem (por exemplo, Wikimedia Commons, Unsplash ou sites de estúdios e de imprensa) e os vídeos são incorporados do YouTube em modo de privacidade aprimorada (youtube-nocookie.com). Ao carregar esses itens, esses serviços recebem o seu endereço de IP e seguem as próprias regras de privacidade. Os botões de compartilhar são links comuns: só enviam algo à rede social se você clicar.</p>
@@ANUNCIOS@@<h2>Transferência internacional</h2>
<p>Google, Cloudflare e OneSignal podem tratar dados em servidores fora do Brasil, com as garantias previstas nas próprias políticas e na LGPD.</p>
<h2>E-mails que você nos envia</h2>
<p>Se você escrever para a gente, usamos o seu e-mail apenas para responder e guardamos a conversa só pelo tempo necessário. Não vendemos nem repassamos dados a ninguém.</p>
<h2>Seus direitos</h2>
<p>Pela LGPD, você pode pedir a confirmação de que tratamos dados seus, o acesso a eles, a correção, a anonimização ou a eliminação, informações sobre com quem foram compartilhados e a revogação do consentimento. Escreva para <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Você também pode reclamar à Autoridade Nacional de Proteção de Dados (ANPD).</p>
<h2>Crianças e adolescentes</h2>
<p>Não pedimos nem coletamos de propósito dados que identifiquem crianças ou adolescentes. Se você é responsável e acredita que recebemos dados de um menor, fale com a gente para que sejam apagados.</p>
<h2>Mudanças nesta política</h2>
<p>Quando algo mudar no funcionamento do site, atualizamos esta página e a data no topo.@@MUDANCA@@</p>""")
ANUNCIOS["pt"] = """<h2>Anúncios (Google AdSense)</h2>
<p>O site exibe anúncios do Google AdSense, que mantêm o conteúdo gratuito. O Google e seus parceiros podem usar cookies e identificadores do aparelho para mostrar anúncios, inclusive personalizados, limitar repetições e medir resultados. Os anúncios só carregam depois do &ldquo;Aceitar&rdquo; no aviso de cookies; se você recusar, o site funciona normalmente, sem anúncios. Para visitantes do Espaço Econômico Europeu, do Reino Unido e da Suíça, o consentimento é pedido por uma plataforma de gestão de consentimento certificada pelo Google. Você pode mudar a sua escolha em &ldquo;Preferências de cookies&rdquo;, no rodapé, e gerenciar a personalização em <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. Saiba como o Google usa esses dados em <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["pt"] = " Hoje o site não exibe anúncios e não usa cookies de publicidade."
MUDANCA["pt"] = " Antes de passarmos a exibir anúncios, esta política será atualizada para explicar como eles funcionam."

# ------------------------------------------------------------------ English
PRIV["en"] = ("Privacy policy", "How ALOHA NOTÍCIAS handles the data of people who visit the site.", """
<p>Last updated: November 9, 2026. This page explains, in plain words, what data is processed when you visit ALOHA NOTÍCIAS (alohanoticias.com), why, and how you control it. We follow Brazil's General Data Protection Law (LGPD, Law 13,709/2018).</p>
<h2>Who is responsible</h2>
<p>ALOHA NOTÍCIAS is responsible for the data processing described here. For any privacy matter, write to <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>What we don't collect</h2>
<p>The site has no sign-up, no reader login and no form asking for your details. We don't know your name or email unless you write to us.@@SEMADS@@</p>
<h2>Visit statistics (Google Analytics)</h2>
<p>We use Google Analytics 4 to see how many people read each page, on what kind of device, from which country or approximate city, and where the visit came from (a search, a social network, our Telegram channel or a partner link, identified by tags in the address). Google Analytics uses cookies and browser identifiers. We receive aggregated numbers and do not use this data to identify you.</p>
<p>In the European Union, the European Economic Area, the UK and Switzerland, measurement only starts after you click &ldquo;Accept&rdquo; in the cookie notice. In other countries, including Brazil, it starts when the page loads, based on our legitimate interest in understanding how the site is used. Anywhere, you can turn it off with &ldquo;Decline&rdquo; in the notice or under &ldquo;Cookie preferences&rdquo; in the footer. Data is kept for the retention period set in Google Analytics. Learn more about <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">how Google uses data from partner sites</a>.</p>
<h2>Hosting and security (Cloudflare)</h2>
<p>The site is hosted by Cloudflare. To deliver pages and protect the site from attacks, Cloudflare processes technical data from each request, such as IP address, browser and page requested, and may count visits in aggregate, without cookies.</p>
<h2>What stays in your browser</h2>
<p>We store in your own browser (local storage, not sent to us) your light or dark theme choice, your answer to the cookie notice and which items in the news bell you have already seen. You can erase all of it by clearing this site's data in your browser.</p>
<h2>Notifications</h2>
<p>If you turn on alerts for new articles, the OneSignal service stores an identifier of your browser to send them. Nothing is turned on without your click, and you can switch it off anytime in your browser or phone settings.</p>
<h2>Content from other sites</h2>
<p>Fonts come from Google Fonts. Some photos are shown from their original address (for example Wikimedia Commons, Unsplash or studio and press websites), and videos are embedded from YouTube in enhanced privacy mode (youtube-nocookie.com). When these items load, those services receive your IP address and follow their own privacy rules. Share buttons are plain links: they only send something to a social network if you click them.</p>
@@ANUNCIOS@@<h2>International transfers</h2>
<p>Google, Cloudflare and OneSignal may process data on servers outside Brazil, with the safeguards set out in their own policies and in the LGPD.</p>
<h2>Emails you send us</h2>
<p>If you write to us, we use your email only to reply and keep the conversation only as long as needed. We do not sell or share data with anyone.</p>
<h2>Your rights</h2>
<p>Under the LGPD you can ask us to confirm whether we process your data, to access, correct, anonymize or delete it, to tell you who it was shared with, and to withdraw consent. Write to <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. You can also complain to Brazil's National Data Protection Authority (ANPD) or to the authority in your country.</p>
<h2>Children</h2>
<p>We do not knowingly ask for or collect data that identifies children or teenagers. If you are a parent or guardian and believe we received a minor's data, contact us and we will delete it.</p>
<h2>Changes</h2>
<p>When something changes in how the site works, we update this page and the date at the top.@@MUDANCA@@ The Portuguese version prevails if there is any difference.</p>""")
ANUNCIOS["en"] = """<h2>Ads (Google AdSense)</h2>
<p>The site shows Google AdSense ads, which keep the content free. Google and its partners may use cookies and device identifiers to show ads, including personalized ones, cap how often they repeat and measure results. Ads only load after you click &ldquo;Accept&rdquo; in the cookie notice; if you decline, the site works normally without ads. For visitors in the European Economic Area, the UK and Switzerland, consent is requested through a Google-certified consent management platform. You can change your choice under &ldquo;Cookie preferences&rdquo; in the footer and manage personalization at <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. See how Google uses this data at <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["en"] = " The site currently shows no ads and uses no advertising cookies."
MUDANCA["en"] = " Before we start showing ads, this policy will be updated to explain how they work."

# ------------------------------------------------------------------ Español
PRIV["es"] = ("Política de privacidad", "Cómo ALOHA NOTÍCIAS trata los datos de quienes visitan el sitio.", """
<p>Última actualización: 9 de noviembre de 2026. Esta página explica, sin tecnicismos, qué datos se tratan cuando visitas ALOHA NOTÍCIAS (alohanoticias.com), para qué y cómo puedes controlarlo. Cumplimos la Ley General de Protección de Datos de Brasil (LGPD, Ley 13.709/2018).</p>
<h2>Quién es el responsable</h2>
<p>ALOHA NOTÍCIAS es el responsable del tratamiento de los datos descritos aquí. Para cualquier asunto de privacidad, escribe a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>Lo que no recopilamos</h2>
<p>El sitio no tiene registro, ni inicio de sesión para lectores, ni formularios que pidan tus datos. No sabemos tu nombre ni tu correo, salvo que nos escribas.@@SEMADS@@</p>
<h2>Estadísticas de visitas (Google Analytics)</h2>
<p>Usamos Google Analytics 4 para saber cuántas personas leen cada página, desde qué tipo de dispositivo y desde qué país o ciudad aproximada, y de dónde llegó la visita (una búsqueda, una red social, nuestro canal de Telegram o el enlace de un colaborador, identificados por etiquetas en la dirección). Google Analytics usa cookies e identificadores del navegador. Recibimos cifras agregadas y no usamos estos datos para identificarte.</p>
<p>En la Unión Europea, el Espacio Económico Europeo, el Reino Unido y Suiza, la medición solo empieza después de que pulses &ldquo;Aceptar&rdquo; en el aviso de cookies. En los demás países, incluido Brasil, empieza al abrir la página, con base en nuestro interés legítimo en entender cómo se usa el sitio. En cualquier lugar puedes desactivarla con &ldquo;Rechazar&rdquo; en el aviso o en &ldquo;Preferencias de cookies&rdquo;, en el pie de página. Los datos se conservan durante el plazo configurado en Google Analytics. Más información sobre <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">cómo usa Google los datos de sitios asociados</a>.</p>
<h2>Alojamiento y seguridad (Cloudflare)</h2>
<p>El sitio está alojado en Cloudflare. Para entregar las páginas y proteger el sitio de ataques, Cloudflare trata datos técnicos de cada acceso, como dirección IP, navegador y página solicitada, y puede contar visitas de forma agregada, sin cookies.</p>
<h2>Lo que queda en tu navegador</h2>
<p>Guardamos en tu propio navegador (almacenamiento local, que no se nos envía) tu elección de tema claro u oscuro, tu respuesta al aviso de cookies y qué avisos de la campana de novedades ya viste. Puedes borrarlo todo eliminando los datos de este sitio en el navegador.</p>
<h2>Notificaciones</h2>
<p>Si activas los avisos de nuevos artículos, el servicio OneSignal guarda un identificador de tu navegador para enviarlos. Nada se activa sin tu clic, y puedes desactivarlo cuando quieras en la configuración del navegador o del móvil.</p>
<h2>Contenido de otros sitios</h2>
<p>Las fuentes tipográficas vienen de Google Fonts. Algunas fotos se muestran desde su dirección original (por ejemplo Wikimedia Commons, Unsplash o sitios de estudios y de prensa) y los vídeos se insertan desde YouTube en modo de privacidad mejorada (youtube-nocookie.com). Al cargarse, esos servicios reciben tu dirección IP y siguen sus propias reglas de privacidad. Los botones de compartir son enlaces normales: solo envían algo a la red social si haces clic.</p>
@@ANUNCIOS@@<h2>Transferencias internacionales</h2>
<p>Google, Cloudflare y OneSignal pueden tratar datos en servidores fuera de Brasil, con las garantías previstas en sus propias políticas y en la LGPD.</p>
<h2>Correos que nos envías</h2>
<p>Si nos escribes, usamos tu correo solo para responder y guardamos la conversación solo el tiempo necesario. No vendemos ni cedemos datos a nadie.</p>
<h2>Tus derechos</h2>
<p>Según la LGPD puedes pedirnos que confirmemos si tratamos tus datos, acceder a ellos, corregirlos, anonimizarlos o eliminarlos, saber con quién se compartieron y retirar tu consentimiento. Escribe a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. También puedes reclamar ante la Autoridad Nacional de Protección de Datos de Brasil (ANPD) o ante la autoridad de tu país.</p>
<h2>Menores</h2>
<p>No pedimos ni recopilamos a sabiendas datos que identifiquen a niños o adolescentes. Si eres padre, madre o tutor y crees que recibimos datos de un menor, escríbenos y los borraremos.</p>
<h2>Cambios</h2>
<p>Cuando algo cambie en el funcionamiento del sitio, actualizaremos esta página y la fecha de arriba.@@MUDANCA@@ Si hay diferencias, prevalece la versión en portugués.</p>""")
ANUNCIOS["es"] = """<h2>Publicidad (Google AdSense)</h2>
<p>El sitio muestra anuncios de Google AdSense, que mantienen el contenido gratuito. Google y sus socios pueden usar cookies e identificadores del dispositivo para mostrar anuncios, también personalizados, limitar repeticiones y medir resultados. Los anuncios solo se cargan después de &ldquo;Aceptar&rdquo; en el aviso de cookies; si rechazas, el sitio funciona con normalidad y sin anuncios. Para visitantes del Espacio Económico Europeo, el Reino Unido y Suiza, el consentimiento se solicita mediante una plataforma de gestión del consentimiento certificada por Google. Puedes cambiar tu elección en &ldquo;Preferencias de cookies&rdquo;, en el pie de página, y gestionar la personalización en <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. Más información en <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["es"] = " Hoy el sitio no muestra anuncios ni usa cookies publicitarias."
MUDANCA["es"] = " Antes de empezar a mostrar anuncios, actualizaremos esta política para explicar cómo funcionan."

# ------------------------------------------------------------------ Français
PRIV["fr"] = ("Politique de confidentialité", "Comment ALOHA NOTÍCIAS traite les données des visiteurs du site.", """
<p>Dernière mise à jour : 9 novembre 2026. Cette page explique simplement quelles données sont traitées lorsque vous visitez ALOHA NOTÍCIAS (alohanoticias.com), dans quel but et comment vous gardez la main. Nous appliquons la loi brésilienne de protection des données (LGPD, loi 13.709/2018).</p>
<h2>Responsable du traitement</h2>
<p>ALOHA NOTÍCIAS est responsable des traitements décrits ici. Pour toute question de confidentialité, écrivez à <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>Ce que nous ne collectons pas</h2>
<p>Le site n'a ni inscription, ni compte lecteur, ni formulaire demandant vos coordonnées. Nous ne connaissons ni votre nom ni votre e-mail, sauf si vous nous écrivez.@@SEMADS@@</p>
<h2>Mesure d'audience (Google Analytics)</h2>
<p>Nous utilisons Google Analytics 4 pour savoir combien de personnes lisent chaque page, sur quel type d'appareil, depuis quel pays ou quelle ville approximative, et d'où vient la visite (moteur de recherche, réseau social, notre canal Telegram ou lien d'un partenaire, repérés par des balises dans l'adresse). Google Analytics utilise des cookies et des identifiants du navigateur. Nous recevons des chiffres agrégés et ne nous en servons pas pour vous identifier.</p>
<p>Dans l'Union européenne, l'Espace économique européen, au Royaume-Uni et en Suisse, la mesure ne commence qu'après un clic sur «&nbsp;Accepter&nbsp;» dans le bandeau cookies. Ailleurs, y compris au Brésil, elle démarre à l'ouverture de la page, sur la base de notre intérêt légitime à comprendre l'usage du site. Partout, vous pouvez la désactiver avec «&nbsp;Refuser&nbsp;» ou via «&nbsp;Préférences de cookies&nbsp;» en bas de page. Les données sont conservées pendant la durée configurée dans Google Analytics. En savoir plus sur <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">l'utilisation des données des sites partenaires par Google</a>.</p>
<h2>Hébergement et sécurité (Cloudflare)</h2>
<p>Le site est hébergé par Cloudflare. Pour servir les pages et protéger le site contre les attaques, Cloudflare traite des données techniques de chaque requête (adresse IP, navigateur, page demandée) et peut compter les visites de façon agrégée, sans cookies.</p>
<h2>Ce qui reste dans votre navigateur</h2>
<p>Nous enregistrons dans votre propre navigateur (stockage local, qui ne nous est pas transmis) votre choix de thème clair ou sombre, votre réponse au bandeau cookies et les alertes de la cloche que vous avez déjà vues. Vous pouvez tout effacer en supprimant les données de ce site dans votre navigateur.</p>
<h2>Notifications</h2>
<p>Si vous activez les alertes de nouveaux articles, le service OneSignal enregistre un identifiant de votre navigateur pour les envoyer. Rien n'est activé sans votre clic, et vous pouvez les couper à tout moment dans les réglages du navigateur ou du téléphone.</p>
<h2>Contenus d'autres sites</h2>
<p>Les polices viennent de Google Fonts. Certaines photos s'affichent depuis leur adresse d'origine (par exemple Wikimedia Commons, Unsplash ou des sites de studios et de presse) et les vidéos sont intégrées depuis YouTube en mode de confidentialité renforcée (youtube-nocookie.com). Au chargement, ces services reçoivent votre adresse IP et appliquent leurs propres règles. Les boutons de partage sont de simples liens : ils n'envoient rien au réseau social sans votre clic.</p>
@@ANUNCIOS@@<h2>Transferts internationaux</h2>
<p>Google, Cloudflare et OneSignal peuvent traiter des données sur des serveurs hors du Brésil, avec les garanties prévues par leurs politiques et par la LGPD.</p>
<h2>E-mails que vous nous envoyez</h2>
<p>Si vous nous écrivez, votre e-mail sert uniquement à vous répondre, et l'échange n'est conservé que le temps nécessaire. Nous ne vendons ni ne cédons de données.</p>
<h2>Vos droits</h2>
<p>Vous pouvez nous demander de confirmer si nous traitons vos données, d'y accéder, de les corriger, de les anonymiser ou de les supprimer, de savoir avec qui elles ont été partagées et de retirer votre consentement. Écrivez à <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Vous pouvez aussi saisir l'autorité brésilienne (ANPD) ou celle de votre pays.</p>
<h2>Mineurs</h2>
<p>Nous ne demandons ni ne collectons sciemment de données identifiant des enfants ou des adolescents. Si vous êtes parent et pensez que nous avons reçu des données d'un mineur, contactez-nous pour les faire supprimer.</p>
<h2>Modifications</h2>
<p>Quand le fonctionnement du site change, nous mettons à jour cette page et la date ci-dessus.@@MUDANCA@@ En cas de différence, la version portugaise fait foi.</p>""")
ANUNCIOS["fr"] = """<h2>Publicité (Google AdSense)</h2>
<p>Le site affiche des annonces Google AdSense, qui permettent de garder le contenu gratuit. Google et ses partenaires peuvent utiliser des cookies et des identifiants d'appareil pour afficher des annonces, y compris personnalisées, limiter leur répétition et mesurer leurs résultats. Les annonces ne se chargent qu'après «&nbsp;Accepter&nbsp;» ; si vous refusez, le site fonctionne normalement, sans publicité. Pour les visiteurs de l'Espace économique européen, du Royaume-Uni et de la Suisse, le consentement est recueilli par une plateforme de gestion du consentement certifiée par Google. Vous pouvez changer d'avis via «&nbsp;Préférences de cookies&nbsp;» et gérer la personnalisation sur <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. Détails sur <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["fr"] = " Aujourd'hui, le site n'affiche pas de publicité et n'utilise pas de cookies publicitaires."
MUDANCA["fr"] = " Avant d'afficher des publicités, nous mettrons cette politique à jour pour expliquer leur fonctionnement."

# ------------------------------------------------------------------ Deutsch
PRIV["de"] = ("Datenschutzerklärung", "Wie ALOHA NOTÍCIAS mit den Daten der Besucherinnen und Besucher umgeht.", """
<p>Stand: 9. November 2026. Diese Seite erklärt verständlich, welche Daten verarbeitet werden, wenn Sie ALOHA NOTÍCIAS (alohanoticias.com) besuchen, wozu und wie Sie das steuern. Wir richten uns nach dem brasilianischen Datenschutzgesetz (LGPD, Gesetz 13.709/2018).</p>
<h2>Verantwortlicher</h2>
<p>Verantwortlich für die hier beschriebene Verarbeitung ist ALOHA NOTÍCIAS. Bei Fragen zum Datenschutz schreiben Sie an <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>Was wir nicht erheben</h2>
<p>Die Website hat keine Registrierung, kein Leserkonto und kein Formular, das nach Ihren Daten fragt. Wir kennen weder Ihren Namen noch Ihre E-Mail-Adresse, außer Sie schreiben uns.@@SEMADS@@</p>
<h2>Besuchsstatistik (Google Analytics)</h2>
<p>Wir nutzen Google Analytics 4, um zu sehen, wie viele Menschen eine Seite lesen, mit welchem Gerätetyp, aus welchem Land oder ungefähr welcher Stadt und woher der Besuch kam (Suche, soziales Netzwerk, unser Telegram-Kanal oder ein Partnerlink, erkennbar an Kennungen in der Adresse). Google Analytics verwendet Cookies und Browser-Kennungen. Wir erhalten zusammengefasste Zahlen und nutzen sie nicht, um Sie zu identifizieren.</p>
<p>In der Europäischen Union, im Europäischen Wirtschaftsraum, im Vereinigten Königreich und in der Schweiz beginnt die Messung erst, nachdem Sie im Cookie-Hinweis auf &bdquo;Akzeptieren&ldquo; geklickt haben. In anderen Ländern, auch in Brasilien, beginnt sie beim Laden der Seite, gestützt auf unser berechtigtes Interesse, die Nutzung der Website zu verstehen. Überall können Sie sie mit &bdquo;Ablehnen&ldquo; oder über &bdquo;Cookie-Einstellungen&ldquo; in der Fußzeile abschalten. Die Daten werden für die in Google Analytics eingestellte Aufbewahrungsdauer gespeichert. Mehr dazu, <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">wie Google Daten von Partnerwebsites nutzt</a>.</p>
<h2>Hosting und Sicherheit (Cloudflare)</h2>
<p>Die Website wird von Cloudflare gehostet. Um Seiten auszuliefern und Angriffe abzuwehren, verarbeitet Cloudflare technische Daten jedes Aufrufs, etwa IP-Adresse, Browser und aufgerufene Seite, und kann Besuche zusammengefasst und ohne Cookies zählen.</p>
<h2>Was in Ihrem Browser bleibt</h2>
<p>Im eigenen Browser (lokaler Speicher, der nicht an uns gesendet wird) speichern wir Ihre Wahl von hellem oder dunklem Design, Ihre Antwort auf den Cookie-Hinweis und welche Meldungen der Neuigkeiten-Glocke Sie schon gesehen haben. Sie können alles löschen, indem Sie die Daten dieser Website im Browser entfernen.</p>
<h2>Benachrichtigungen</h2>
<p>Wenn Sie Hinweise auf neue Artikel aktivieren, speichert der Dienst OneSignal eine Kennung Ihres Browsers, um sie zu senden. Ohne Ihren Klick wird nichts aktiviert, und Sie können es jederzeit in den Browser- oder Telefoneinstellungen abschalten.</p>
<h2>Inhalte anderer Websites</h2>
<p>Schriftarten stammen von Google Fonts. Manche Fotos werden von ihrer Ursprungsadresse geladen (etwa Wikimedia Commons, Unsplash oder Websites von Studios und Medien), Videos werden von YouTube im erweiterten Datenschutzmodus (youtube-nocookie.com) eingebettet. Beim Laden erhalten diese Dienste Ihre IP-Adresse und wenden eigene Datenschutzregeln an. Teilen-Schaltflächen sind einfache Links: Sie senden nur etwas an ein Netzwerk, wenn Sie klicken.</p>
@@ANUNCIOS@@<h2>Übermittlung ins Ausland</h2>
<p>Google, Cloudflare und OneSignal können Daten auf Servern außerhalb Brasiliens verarbeiten, mit den in ihren Richtlinien und im LGPD vorgesehenen Garantien.</p>
<h2>E-Mails an uns</h2>
<p>Wenn Sie uns schreiben, nutzen wir Ihre E-Mail-Adresse nur für die Antwort und bewahren den Austausch nur so lange wie nötig auf. Wir verkaufen keine Daten und geben sie nicht weiter.</p>
<h2>Ihre Rechte</h2>
<p>Sie können Bestätigung verlangen, ob wir Daten von Ihnen verarbeiten, sowie Auskunft, Berichtigung, Anonymisierung oder Löschung, Informationen darüber, mit wem sie geteilt wurden, und den Widerruf Ihrer Einwilligung. Schreiben Sie an <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Sie können sich auch bei der brasilianischen Datenschutzbehörde (ANPD) oder der Aufsichtsbehörde Ihres Landes beschweren.</p>
<h2>Kinder und Jugendliche</h2>
<p>Wir fragen nicht wissentlich nach Daten, die Kinder oder Jugendliche identifizieren, und erheben sie nicht. Wenn Sie als Elternteil glauben, dass wir Daten eines Minderjährigen erhalten haben, melden Sie sich, dann löschen wir sie.</p>
<h2>Änderungen</h2>
<p>Wenn sich an der Funktionsweise der Website etwas ändert, aktualisieren wir diese Seite und das Datum oben.@@MUDANCA@@ Bei Abweichungen gilt die portugiesische Fassung.</p>""")
ANUNCIOS["de"] = """<h2>Werbung (Google AdSense)</h2>
<p>Die Website zeigt Anzeigen von Google AdSense, die das Angebot kostenlos halten. Google und seine Partner können Cookies und Gerätekennungen nutzen, um Anzeigen auszuliefern, auch personalisierte, Wiederholungen zu begrenzen und Ergebnisse zu messen. Anzeigen werden erst nach &bdquo;Akzeptieren&ldquo; geladen; wenn Sie ablehnen, funktioniert die Website normal ohne Werbung. Für Besucher aus dem Europäischen Wirtschaftsraum, dem Vereinigten Königreich und der Schweiz wird die Einwilligung über eine von Google zertifizierte Plattform zur Einwilligungsverwaltung eingeholt. Sie können Ihre Wahl unter &bdquo;Cookie-Einstellungen&ldquo; ändern und die Personalisierung unter <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a> verwalten. Details unter <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["de"] = " Derzeit zeigt die Website keine Werbung und nutzt keine Werbe-Cookies."
MUDANCA["de"] = " Bevor wir Werbung zeigen, wird diese Erklärung aktualisiert und erläutert, wie sie funktioniert."

# ------------------------------------------------------------------ Italiano
PRIV["it"] = ("Informativa sulla privacy", "Come ALOHA NOTÍCIAS tratta i dati di chi visita il sito.", """
<p>Ultimo aggiornamento: 9 novembre 2026. Questa pagina spiega in modo semplice quali dati vengono trattati quando visiti ALOHA NOTÍCIAS (alohanoticias.com), a che scopo e come puoi controllarlo. Seguiamo la legge brasiliana sulla protezione dei dati (LGPD, legge 13.709/2018).</p>
<h2>Titolare del trattamento</h2>
<p>Il titolare dei trattamenti descritti qui è ALOHA NOTÍCIAS. Per qualsiasi questione di privacy scrivi a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>Cosa non raccogliamo</h2>
<p>Il sito non ha registrazione, account per i lettori né moduli che chiedono i tuoi dati. Non conosciamo il tuo nome né la tua e-mail, a meno che tu non ci scriva.@@SEMADS@@</p>
<h2>Statistiche delle visite (Google Analytics)</h2>
<p>Usiamo Google Analytics 4 per sapere quante persone leggono ogni pagina, con che tipo di dispositivo, da quale paese o città approssimativa e da dove arriva la visita (una ricerca, un social network, il nostro canale Telegram o il link di un partner, riconosciuti da etichette nell'indirizzo). Google Analytics usa cookie e identificatori del browser. Riceviamo numeri aggregati e non li usiamo per identificarti.</p>
<p>Nell'Unione europea, nello Spazio economico europeo, nel Regno Unito e in Svizzera la misurazione parte solo dopo che fai clic su &laquo;Accetta&raquo; nell'avviso sui cookie. Negli altri paesi, Brasile compreso, parte all'apertura della pagina, sulla base del nostro legittimo interesse a capire come viene usato il sito. Ovunque puoi disattivarla con &laquo;Rifiuta&raquo; o da &laquo;Preferenze cookie&raquo; a fondo pagina. I dati sono conservati per il periodo impostato in Google Analytics. Scopri <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">come Google usa i dati dei siti partner</a>.</p>
<h2>Hosting e sicurezza (Cloudflare)</h2>
<p>Il sito è ospitato da Cloudflare. Per distribuire le pagine e proteggere il sito dagli attacchi, Cloudflare tratta dati tecnici di ogni richiesta, come indirizzo IP, browser e pagina richiesta, e può contare le visite in forma aggregata, senza cookie.</p>
<h2>Cosa resta nel tuo browser</h2>
<p>Salviamo nel tuo browser (archiviazione locale, che non ci viene inviata) la scelta del tema chiaro o scuro, la risposta all'avviso sui cookie e quali avvisi della campanella delle novità hai già visto. Puoi cancellare tutto eliminando i dati di questo sito dal browser.</p>
<h2>Notifiche</h2>
<p>Se attivi gli avvisi sui nuovi articoli, il servizio OneSignal salva un identificatore del tuo browser per inviarli. Nulla si attiva senza il tuo clic, e puoi disattivarli quando vuoi dalle impostazioni del browser o del telefono.</p>
<h2>Contenuti di altri siti</h2>
<p>I caratteri provengono da Google Fonts. Alcune foto sono mostrate dal loro indirizzo originale (per esempio Wikimedia Commons, Unsplash o siti di studi e testate) e i video sono incorporati da YouTube in modalità di privacy avanzata (youtube-nocookie.com). Durante il caricamento questi servizi ricevono il tuo indirizzo IP e seguono le proprie regole. I pulsanti di condivisione sono semplici link: inviano qualcosa al social solo se fai clic.</p>
@@ANUNCIOS@@<h2>Trasferimenti internazionali</h2>
<p>Google, Cloudflare e OneSignal possono trattare dati su server fuori dal Brasile, con le garanzie previste dalle loro informative e dalla LGPD.</p>
<h2>E-mail che ci invii</h2>
<p>Se ci scrivi, usiamo la tua e-mail solo per risponderti e conserviamo lo scambio solo per il tempo necessario. Non vendiamo né cediamo dati a nessuno.</p>
<h2>I tuoi diritti</h2>
<p>Puoi chiederci di confermare se trattiamo tuoi dati, di accedervi, correggerli, anonimizzarli o cancellarli, di sapere con chi sono stati condivisi e di revocare il consenso. Scrivi a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Puoi anche rivolgerti all'autorità brasiliana (ANPD) o al Garante del tuo paese.</p>
<h2>Minori</h2>
<p>Non chiediamo né raccogliamo consapevolmente dati che identificano bambini o adolescenti. Se sei un genitore e pensi che abbiamo ricevuto dati di un minore, contattaci e li cancelleremo.</p>
<h2>Modifiche</h2>
<p>Quando cambia qualcosa nel funzionamento del sito, aggiorniamo questa pagina e la data in alto.@@MUDANCA@@ In caso di differenze prevale la versione in portoghese.</p>""")
ANUNCIOS["it"] = """<h2>Pubblicità (Google AdSense)</h2>
<p>Il sito mostra annunci Google AdSense, che permettono di mantenere gratuiti i contenuti. Google e i suoi partner possono usare cookie e identificatori del dispositivo per mostrare annunci, anche personalizzati, limitarne la ripetizione e misurarne i risultati. Gli annunci si caricano solo dopo &laquo;Accetta&raquo;; se rifiuti, il sito funziona normalmente senza pubblicità. Per i visitatori dello Spazio economico europeo, del Regno Unito e della Svizzera, il consenso è raccolto tramite una piattaforma di gestione del consenso certificata da Google. Puoi cambiare scelta da &laquo;Preferenze cookie&raquo; e gestire la personalizzazione su <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. Dettagli su <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["it"] = " Oggi il sito non mostra pubblicità e non usa cookie pubblicitari."
MUDANCA["it"] = " Prima di mostrare pubblicità aggiorneremo questa informativa per spiegare come funziona."

# ------------------------------------------------------------------ 日本語
PRIV["ja"] = ("プライバシーポリシー", "ALOHA NOTÍCIAS が訪問者のデータをどのように扱うか。", """
<p>最終更新日：2026年11月9日。このページでは、ALOHA NOTÍCIAS（alohanoticias.com）を訪れたときにどのようなデータが、何のために扱われ、どうすれば管理できるかを分かりやすく説明します。当サイトはブラジルの個人データ保護法（LGPD、法律第13.709/2018号）に従っています。</p>
<h2>責任者</h2>
<p>ここに記載するデータの取り扱いの責任者は ALOHA NOTÍCIAS です。プライバシーに関するお問い合わせは <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a> までお送りください。</p>
<h2>収集しないもの</h2>
<p>当サイトには会員登録、読者ログイン、個人情報を求めるフォームはありません。ご連絡をいただかない限り、お名前やメールアドレスは分かりません。@@SEMADS@@</p>
<h2>アクセス統計（Google アナリティクス）</h2>
<p>各ページを何人が読んだか、どの種類の端末から、どの国やおおよその都市から、どこから訪れたか（検索、SNS、当サイトの Telegram チャンネル、提携先のリンクなど。アドレスに付けたタグで判別します）を知るために Google アナリティクス 4 を使用しています。Google アナリティクスはクッキーとブラウザの識別子を使います。私たちが受け取るのは集計された数値で、あなたを特定するためには使いません。</p>
<p>欧州連合、欧州経済領域、英国、スイスでは、クッキーの案内で「同意する」をクリックした後にのみ計測が始まります。ブラジルを含むその他の国では、サイトの利用状況を把握するという正当な利益に基づき、ページを開いた時点で計測が始まります。どの地域でも、案内の「拒否する」またはフッターの「クッキーの設定」から停止できます。データは Google アナリティクスで設定した保存期間だけ保管されます。詳しくは<a href="https://policies.google.com/technologies/partner-sites" rel="noopener">Google によるパートナーサイトのデータの使用</a>をご覧ください。</p>
<h2>ホスティングとセキュリティ（Cloudflare）</h2>
<p>当サイトは Cloudflare でホスティングされています。ページを配信し攻撃から守るため、Cloudflare は各アクセスの技術的なデータ（IP アドレス、ブラウザ、要求されたページなど）を処理し、クッキーを使わずに訪問数を集計することがあります。</p>
<h2>ブラウザに保存されるもの</h2>
<p>ライト／ダークテーマの選択、クッキーの案内への回答、新着ベルのどの通知を見たかを、あなたのブラウザ内（ローカルストレージ。私たちには送信されません）に保存します。ブラウザでこのサイトのデータを削除すれば、すべて消去できます。</p>
<h2>通知</h2>
<p>新着記事の通知をオンにすると、送信のために OneSignal があなたのブラウザの識別子を保存します。クリックしない限り何もオンになりません。ブラウザやスマートフォンの設定でいつでもオフにできます。</p>
<h2>他サイトのコンテンツ</h2>
<p>フォントは Google Fonts から読み込みます。一部の写真は元のアドレス（Wikimedia Commons、Unsplash、スタジオや報道機関のサイトなど）から表示し、動画はプライバシー強化モードの YouTube（youtube-nocookie.com）から埋め込んでいます。読み込みの際、これらのサービスはあなたの IP アドレスを受け取り、それぞれのルールに従います。共有ボタンは通常のリンクで、クリックしない限り SNS に何も送りません。</p>
@@ANUNCIOS@@<h2>国外への移転</h2>
<p>Google、Cloudflare、OneSignal はブラジル国外のサーバーでデータを処理することがあり、各社のポリシーと LGPD に定める保護措置が適用されます。</p>
<h2>お送りいただいたメール</h2>
<p>ご連絡いただいた場合、メールアドレスは返信のためだけに使い、やり取りは必要な期間だけ保管します。データの販売や第三者への提供は行いません。</p>
<h2>あなたの権利</h2>
<p>データを扱っているかの確認、アクセス、訂正、匿名化または削除、共有先についての情報、同意の撤回を求めることができます。<a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a> までご連絡ください。ブラジルの国家データ保護機関（ANPD）またはお住まいの国の機関に申し立てることもできます。</p>
<h2>子どもについて</h2>
<p>子どもや未成年者を特定するデータを意図的に求めたり収集したりすることはありません。保護者の方で、未成年者のデータを受け取ったと思われる場合はご連絡ください。削除します。</p>
<h2>変更</h2>
<p>サイトの仕組みに変更があった場合は、このページと上部の日付を更新します。@@MUDANCA@@内容に違いがある場合はポルトガル語版が優先されます。</p>""")
ANUNCIOS["ja"] = """<h2>広告（Google AdSense）</h2>
<p>当サイトはコンテンツを無料で提供するため、Google AdSense の広告を表示しています。Google とそのパートナーは、パーソナライズ広告を含む広告の表示、表示回数の制限、効果測定のためにクッキーや端末の識別子を使用することがあります。広告はクッキーの案内で「同意する」をクリックした後にのみ読み込まれ、拒否した場合も広告なしで通常どおり利用できます。欧州経済領域、英国、スイスからの訪問者には、Google 認定の同意管理プラットフォームで同意を確認します。選択はフッターの「クッキーの設定」で変更でき、パーソナライズは <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a> で管理できます。詳しくは <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a> をご覧ください。</p>
"""
SEMADS["ja"] = "現在、当サイトは広告を表示しておらず、広告用クッキーも使用していません。"
MUDANCA["ja"] = "広告を表示する前に、その仕組みを説明するためこのポリシーを更新します。"

# ------------------------------------------------------------------ 中文
PRIV["zh"] = ("隐私政策", "ALOHA NOTÍCIAS 如何处理网站访问者的数据。", """
<p>最后更新：2026年11月9日。本页用通俗的语言说明，当你访问 ALOHA NOTÍCIAS（alohanoticias.com）时，哪些数据会被处理、用途是什么，以及你如何控制。我们遵守巴西《通用数据保护法》（LGPD，第 13.709/2018 号法律）。</p>
<h2>负责人</h2>
<p>本页所述数据处理的负责人是 ALOHA NOTÍCIAS。任何隐私问题，请写信至 <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>。</p>
<h2>我们不收集的内容</h2>
<p>本站没有注册、读者登录，也没有索取个人信息的表单。除非你给我们写信，否则我们不知道你的姓名或电子邮箱。@@SEMADS@@</p>
<h2>访问统计（Google Analytics）</h2>
<p>我们使用 Google Analytics 4 了解每个页面有多少人阅读、使用何种设备、来自哪个国家或大致城市，以及访问从哪里来（搜索、社交网络、我们的 Telegram 频道或合作伙伴链接，通过网址中的标签识别）。Google Analytics 会使用 Cookie 和浏览器标识符。我们收到的是汇总数字，不会用来识别你的身份。</p>
<p>在欧盟、欧洲经济区、英国和瑞士，只有在你点击 Cookie 提示中的“接受”后才开始统计。在包括巴西在内的其他国家，基于我们了解网站使用情况的正当利益，页面打开时即开始统计。在任何地区，你都可以点击“拒绝”或页脚的“Cookie 偏好设置”将其关闭。数据按 Google Analytics 中设置的保留期限保存。了解<a href="https://policies.google.com/technologies/partner-sites" rel="noopener">Google 如何使用合作网站的数据</a>。</p>
<h2>托管与安全（Cloudflare）</h2>
<p>本站由 Cloudflare 托管。为了传送页面并防御攻击，Cloudflare 会处理每次访问的技术数据（如 IP 地址、浏览器和请求的页面），并可能在不使用 Cookie 的情况下汇总统计访问量。</p>
<h2>保存在你浏览器中的内容</h2>
<p>我们会在你自己的浏览器中（本地存储，不会发送给我们）保存你选择的浅色或深色主题、你对 Cookie 提示的选择，以及你已看过的新闻铃铛通知。在浏览器中清除本站数据即可全部删除。</p>
<h2>通知</h2>
<p>如果你开启新文章提醒，OneSignal 服务会保存你浏览器的一个标识符用于发送通知。不经你点击不会开启任何功能，你也可以随时在浏览器或手机设置中关闭。</p>
<h2>来自其他网站的内容</h2>
<p>字体来自 Google Fonts。部分图片从其原始地址加载（例如 Wikimedia Commons、Unsplash 或制片公司和媒体网站），视频以增强隐私模式从 YouTube（youtube-nocookie.com）嵌入。加载时，这些服务会收到你的 IP 地址，并遵循各自的隐私规则。分享按钮只是普通链接，只有你点击时才会向社交网络发送内容。</p>
@@ANUNCIOS@@<h2>跨境传输</h2>
<p>Google、Cloudflare 和 OneSignal 可能在巴西境外的服务器上处理数据，并适用其政策和 LGPD 规定的保障措施。</p>
<h2>你发给我们的邮件</h2>
<p>如果你给我们写信，我们只用你的邮箱回复，并且只在必要期间保留往来记录。我们不会出售或向任何人提供数据。</p>
<h2>你的权利</h2>
<p>你可以要求我们确认是否处理你的数据，并要求访问、更正、匿名化或删除数据，了解数据与谁共享，以及撤回同意。请写信至 <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>。你也可以向巴西国家数据保护局（ANPD）或你所在国家的主管机构投诉。</p>
<h2>未成年人</h2>
<p>我们不会故意索取或收集可识别儿童或青少年身份的数据。如果你是家长或监护人，认为我们收到了未成年人的数据，请联系我们，我们会将其删除。</p>
<h2>变更</h2>
<p>网站运作方式发生变化时，我们会更新本页和顶部日期。@@MUDANCA@@如有差异，以葡萄牙语版本为准。</p>""")
ANUNCIOS["zh"] = """<h2>广告（Google AdSense）</h2>
<p>本站展示 Google AdSense 广告，以保持内容免费。Google 及其合作伙伴可能使用 Cookie 和设备标识符来展示广告（包括个性化广告）、限制重复展示并衡量效果。只有在你点击 Cookie 提示中的“接受”后才会加载广告；如果拒绝，网站照常使用，不显示广告。对于来自欧洲经济区、英国和瑞士的访问者，将通过经 Google 认证的同意管理平台征求同意。你可以在页脚的“Cookie 偏好设置”中更改选择，并在 <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a> 管理个性化设置。详情见 <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>。</p>
"""
SEMADS["zh"] = "目前本站不展示广告，也不使用广告 Cookie。"
MUDANCA["zh"] = "在开始展示广告之前，我们会更新本政策，说明广告如何运作。"

# ------------------------------------------------------------------ العربية
PRIV["ar"] = ("سياسة الخصوصية", "كيف يتعامل موقع ALOHA NOTÍCIAS مع بيانات زواره.", """
<p>آخر تحديث: 9 نوفمبر 2026. توضح هذه الصفحة بلغة بسيطة البيانات التي تُعالَج عند زيارتك موقع ALOHA NOTÍCIAS (alohanoticias.com)، والغرض منها، وكيف تتحكم فيها. نلتزم بالقانون البرازيلي العام لحماية البيانات (LGPD، القانون 13.709/2018).</p>
<h2>الجهة المسؤولة</h2>
<p>الجهة المسؤولة عن معالجة البيانات الموصوفة هنا هي ALOHA NOTÍCIAS. لأي مسألة تتعلق بالخصوصية، راسلنا على <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>
<h2>ما لا نجمعه</h2>
<p>لا يوجد في الموقع تسجيل ولا حساب للقراء ولا نموذج يطلب بياناتك. لا نعرف اسمك ولا بريدك الإلكتروني إلا إذا راسلتنا.@@SEMADS@@</p>
<h2>إحصاءات الزيارات (Google Analytics)</h2>
<p>نستخدم Google Analytics 4 لمعرفة عدد من يقرأ كل صفحة، ونوع الجهاز، والبلد أو المدينة التقريبية، ومصدر الزيارة (بحث، أو شبكة اجتماعية، أو قناتنا على Telegram، أو رابط شريك، نتعرّف عليها من وسوم في العنوان). يستخدم Google Analytics ملفات تعريف الارتباط ومعرّفات المتصفح. نحصل على أرقام مجمّعة ولا نستخدمها للتعرّف على هويتك.</p>
<p>في الاتحاد الأوروبي والمنطقة الاقتصادية الأوروبية والمملكة المتحدة وسويسرا، لا يبدأ القياس إلا بعد النقر على «موافق» في تنبيه ملفات تعريف الارتباط. وفي البلدان الأخرى، ومنها البرازيل، يبدأ عند فتح الصفحة استنادًا إلى مصلحتنا المشروعة في فهم كيفية استخدام الموقع. وفي أي مكان يمكنك إيقافه بالنقر على «رفض» أو من «تفضيلات ملفات تعريف الارتباط» أسفل الصفحة. تُحفظ البيانات طوال مدة الاحتفاظ المضبوطة في Google Analytics. اعرف المزيد عن <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">كيفية استخدام Google لبيانات المواقع الشريكة</a>.</p>
<h2>الاستضافة والأمان (Cloudflare)</h2>
<p>الموقع مستضاف لدى Cloudflare. لتقديم الصفحات وحماية الموقع من الهجمات، تعالج Cloudflare بيانات تقنية لكل طلب، مثل عنوان IP والمتصفح والصفحة المطلوبة، وقد تحصي الزيارات بشكل مجمّع ومن دون ملفات تعريف الارتباط.</p>
<h2>ما يبقى في متصفحك</h2>
<p>نحفظ في متصفحك نفسه (تخزين محلي لا يُرسل إلينا) اختيارك للمظهر الفاتح أو الداكن، وردّك على تنبيه ملفات تعريف الارتباط، والتنبيهات التي رأيتها في جرس الأخبار. يمكنك حذف كل ذلك بمسح بيانات هذا الموقع من المتصفح.</p>
<h2>الإشعارات</h2>
<p>إذا فعّلت تنبيهات المقالات الجديدة، تحفظ خدمة OneSignal معرّفًا لمتصفحك لإرسالها. لا يُفعَّل شيء دون نقرتك، ويمكنك إيقافها في أي وقت من إعدادات المتصفح أو الهاتف.</p>
<h2>محتوى من مواقع أخرى</h2>
<p>الخطوط من Google Fonts. تُعرض بعض الصور من عنوانها الأصلي (مثل Wikimedia Commons وUnsplash ومواقع الاستوديوهات ووسائل الإعلام)، وتُضمَّن مقاطع الفيديو من YouTube في وضع الخصوصية المحسّن (youtube-nocookie.com). عند التحميل تتلقى هذه الخدمات عنوان IP الخاص بك وتطبق قواعدها الخاصة. أزرار المشاركة روابط عادية لا ترسل شيئًا إلى الشبكة الاجتماعية إلا إذا نقرت عليها.</p>
@@ANUNCIOS@@<h2>النقل الدولي</h2>
<p>قد تعالج Google وCloudflare وOneSignal البيانات على خوادم خارج البرازيل، مع الضمانات المنصوص عليها في سياساتها وفي LGPD.</p>
<h2>الرسائل التي ترسلها إلينا</h2>
<p>إذا راسلتنا، نستخدم بريدك للرد فقط ونحتفظ بالمراسلة للمدة اللازمة فقط. لا نبيع البيانات ولا نشاركها مع أحد.</p>
<h2>حقوقك</h2>
<p>يمكنك أن تطلب تأكيد ما إذا كنا نعالج بياناتك، والاطلاع عليها وتصحيحها أو إخفاء هويتها أو حذفها، ومعرفة الجهات التي شوركت معها، وسحب موافقتك. راسلنا على <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. ويمكنك أيضًا تقديم شكوى إلى الهيئة الوطنية البرازيلية لحماية البيانات (ANPD) أو إلى الجهة المختصة في بلدك.</p>
<h2>القاصرون</h2>
<p>لا نطلب ولا نجمع عن قصد بيانات تحدد هوية الأطفال أو المراهقين. إذا كنت وليّ أمر وتعتقد أننا تلقينا بيانات قاصر، فتواصل معنا وسنحذفها.</p>
<h2>التغييرات</h2>
<p>عند تغيّر أي شيء في طريقة عمل الموقع، نحدّث هذه الصفحة والتاريخ أعلاها.@@MUDANCA@@ عند وجود اختلاف، تكون النسخة البرتغالية هي المرجع.</p>""")
ANUNCIOS["ar"] = """<h2>الإعلانات (Google AdSense)</h2>
<p>يعرض الموقع إعلانات Google AdSense التي تُبقي المحتوى مجانيًا. قد تستخدم Google وشركاؤها ملفات تعريف الارتباط ومعرّفات الجهاز لعرض الإعلانات، ومنها الإعلانات المخصّصة، وللحد من تكرارها وقياس نتائجها. لا تُحمَّل الإعلانات إلا بعد النقر على «موافق»؛ وإذا رفضت يعمل الموقع بشكل طبيعي من دون إعلانات. بالنسبة لزوار المنطقة الاقتصادية الأوروبية والمملكة المتحدة وسويسرا، تُطلب الموافقة عبر منصة لإدارة الموافقة معتمدة من Google. يمكنك تغيير اختيارك من «تفضيلات ملفات تعريف الارتباط» وإدارة التخصيص في <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>. التفاصيل في <a href="https://policies.google.com/technologies/ads" rel="noopener">policies.google.com/technologies/ads</a>.</p>
"""
SEMADS["ar"] = " لا يعرض الموقع حاليًا أي إعلانات ولا يستخدم ملفات تعريف ارتباط إعلانية."
MUDANCA["ar"] = " قبل أن نبدأ في عرض الإعلانات، سنحدّث هذه السياسة لشرح طريقة عملها."


def pagina(lang, anuncios_ativos):
    """(titulo, descricao, html) da política no idioma, já com os marcadores trocados."""
    tit, desc, corpo = PRIV.get(lang, PRIV["pt"])
    lang = lang if lang in PRIV else "pt"
    corpo = (corpo.replace("@@ANUNCIOS@@", ANUNCIOS[lang] if anuncios_ativos else "")
                  .replace("@@SEMADS@@", "" if anuncios_ativos else SEMADS[lang])
                  .replace("@@MUDANCA@@", "" if anuncios_ativos else MUDANCA[lang]))
    return tit, desc, corpo
