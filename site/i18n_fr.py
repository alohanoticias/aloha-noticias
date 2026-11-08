"""Français : interface, pages institutionnelles."""
NOME = "Français"
MES = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
DIA = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
ED = {
    "games": ("Jeux vidéo", "Sorties, culture gaming et studios derrière les jeux."),
    "cinema": ("Cinéma et séries", "Sorties, coulisses et tout ce qui entoure la séance."),
    "tecnologia": ("Technologie", "Outils, sécurité numérique et tech du quotidien, sans jargon."),
    "anime": ("Anime", "Anime, manga et culture otaku : les sorties de la saison, les adaptations et ce qui buzze."),
    "curiosidades": ("Curiosités", "Les questions que tout le monde s'est posées, avec des réponses scientifiques."),
}
UI = {
    "Pular para o conteúdo": "Aller au contenu",
    "Início": "Accueil",
    "Buscar": "Rechercher",
    "Alternar tema": "Changer de thème",
    "Abrir menu": "Ouvrir le menu",
    "Editorias": "Rubriques",
    "Idioma / Language": "Langue",
    "Traduzir esta página / Translate": "Langue",
    "Traduzir / Translate": "Langue",
    "Traduzir / Translate:": "Langue :",
    "página inicial": "page d'accueil",
    "Cinema, games e tecnologia explicados com calma, de olho no que importa.": "Cinéma, jeux vidéo et technologie expliqués calmement, en gardant l'œil sur l'essentiel.",
    "Institucional": "À propos du site",
    "Sobre nós": "À propos de nous",
    "Contato e anúncios": "Contact et publicité",
    "Equipe Aloha": "Équipe Aloha",
    "Política editorial": "Politique éditoriale",
    "Termos de uso": "Conditions d'utilisation",
    "Privacidade": "Confidentialité",
    "RSS": "RSS (portugais)",
    "Ilustração": "Illustration",
    "min de leitura": "min de lecture",
    "min": "min",
    "Mais lidas": "Les plus lus",
    "Voltar às notícias anteriores de": "Retour aux articles précédents de",
    "Ver mais notícias de": "Plus d'articles dans",
    "Ver tudo em": "Tout voir dans",
    "Mais em": "Plus dans",
    "Ainda não publicamos matérias nesta editoria. Volte em breve.": "Nous n'avons encore rien publié dans cette rubrique. Revenez bientôt.",
    "Você está em": "Vous êtes ici",
    "Por": "Par",
    "Compartilhe": "Partager",
    "Copiar link": "Copier le lien",
    "Leia também": "À lire aussi",
    "Atualizado em": "Mis à jour le",
    "Atualização:": "Mise à jour :",
    "Compartilhar no": "Partager sur",
    "Assuntos": "Sujets",
    "matéria": "article",
    "matérias": "articles",
    "sobre este assunto.": "sur ce sujet.",
    "Matérias da ALOHA NOTÍCIAS sobre": "Articles d'ALOHA NOTÍCIAS sur",
    "Busque matérias da ALOHA NOTÍCIAS.": "Recherchez parmi les articles d'ALOHA NOTÍCIAS.",
    "Buscar matérias": "Rechercher des articles",
    "Ex.: GTA 6, Vingadores, Switch 2": "Ex. : GTA 6, Avengers, Switch 2",
    "Página não encontrada": "Page introuvable",
    "Essa onda passou": "Cette vague est passée",
    "A página que você procurou não existe ou mudou de endereço.": "La page que vous cherchez n'existe pas ou a changé d'adresse.",
    "Voltar para a página inicial": "Retour à l'accueil",
    "ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia": "ALOHA NOTÍCIAS : actualités, cinéma, jeux vidéo et technologie",
    "Notícias, cinema, games e tecnologia, explicados com calma.": "Actualités, cinéma, jeux vidéo et technologie, expliqués calmement.",
    "Destaques": "À la une",
    "Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.": "Saisissez un sujet, par exemple : GTA 6, Marvel ou cinéma.",
    "Nada encontrado para": "Aucun résultat pour",
    "Tente outra palavra.": "Essayez un autre mot.",
    "matéria encontrada": "article trouvé",
    "matérias encontradas": "articles trouvés",
    "Link copiado": "Lien copié",
    "Copie o endereço na barra do navegador": "Copiez l'adresse dans la barre du navigateur",
    "Aviso de cookies": "Avis sur les cookies",
    "Aceitar": "Accepter",
    "Recusar": "Refuser",
    "Leia esta página em português (idioma original)": "Lire cette page en portugais (langue d'origine)",
    "Esta matéria foi escrita em português e adaptada para o inglês pela equipe.": "Cet article a été écrit en portugais et adapté en français par l'équipe.",
    "Esta página também existe em": "Cette page existe aussi en",
    "Original em português": "Original en portugais",
}
CONSENT = "Nous utilisons des cookies pour afficher des publicités et garder le site gratuit. C'est à vous de choisir : si vous n'acceptez pas, nous ne chargeons pas de publicités."
SABER = "En savoir plus"
PRIV = """<h2>Publicités et cookies</h2>
<p>Ce site affiche des publicités Google AdSense. Avec votre autorisation, Google et ses partenaires peuvent utiliser des cookies et des identifiants d'appareil pour afficher des publicités et mesurer leurs performances. Les publicités ne se chargent qu'après un clic sur &laquo;&nbsp;Accepter&nbsp;&raquo; dans l'avis sur les cookies ; si vous refusez, le site continue de fonctionner normalement, sans publicité. Vous pouvez changer d'avis à tout moment dans les <a href="#" id="reabrir-consent">préférences de cookies</a>.</p>
<p>Découvrez comment Google utilise les données des sites partenaires sur <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. Vous pouvez aussi gérer les annonces personnalisées sur <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.</p>
"""
PAG = {}
PAG["sobre.html"] = ("À propos de nous", "Qui est derrière ALOHA NOTÍCIAS.", """
<p>ALOHA NOTÍCIAS est un site d'actualités brésilien pour celles et ceux qui veulent comprendre ce qui se passe sans le bruit. Nous nous concentrons sur le cinéma, les jeux vidéo et la technologie : sorties, lancements et sujets du moment, avec des faits vérifiés.</p>
<p>Nous écrivons d'abord en portugais. Cette édition française est adaptée par notre équipe pour les lecteurs hors du Brésil ; vous y trouverez donc des dates et des détails de sortie brésiliens expliqués quand cela compte.</p>
<h2>Notre façon de travailler</h2>
<p>Chaque article cite ses sources, distingue les faits de l'opinion et est corrigé ouvertement lorsque nous nous trompons. Les détails figurent dans notre <a href="politica-editorial.html">politique éditoriale</a>.</p>
<h2>Le nom</h2>
<p><em>Aloha</em> est le salut hawaïen, qui signifie aussi affection et respect. C'est ainsi que nous voulons traiter celles et ceux qui nous lisent.</p>
<h2>Nous contacter</h2>
<p>Suggestions, corrections et partenariats : <a href="contato.html">page de contact</a>.</p>""")
PAG["politica-editorial.html"] = ("Politique éditoriale et de corrections", "Comment ALOHA NOTÍCIAS enquête, écrit, illustre et corrige ses articles.", """
<p>Cette page explique, en langage simple, comment le contenu d'ALOHA NOTÍCIAS est fabriqué. Si nous manquons à l'un de ces engagements, nous voulons le savoir.</p>
<h2>Comment nous vérifions</h2>
<p>Nous essayons de confirmer chaque information importante auprès de plusieurs sources avant de publier. Les dates, les prix et les chiffres ne figurent dans le texte que s'ils apparaissent dans les sources consultées, que nous listons à la fin de chaque article. Lorsqu'une information vient d'une seule source ou n'est pas encore confirmée, nous le disons dans le texte.</p>
<h2>Comment nous choisissons les sujets</h2>
<p>Nous privilégions ce qui est d'actualité et utile aux lecteurs : sorties, lancements, dates et nouveautés du cinéma, des jeux vidéo et de la technologie. Nous ne publions pas pour simplement relayer un communiqué. Dans chaque article, nous cherchons à rassembler ce qui est confirmé, à clarifier ce qui reste inconnu et à montrer d'où vient chaque information.</p>
<h2>Rumeurs et fuites</h2>
<p>Les rumeurs, les fuites et les informations de coulisses n'apparaissent que lorsqu'elles sont pertinentes, toujours signalées comme non confirmées et avec la source indiquée. Nous ne traitons pas une rumeur comme un fait.</p>
<h2>Relecture avant publication</h2>
<p>Aucun article n'est mis en ligne sans la relecture et l'approbation d'une personne de l'équipe.</p>
<h2>Images et vidéos</h2>
<p>Nos couvertures sont composées par notre équipe à partir de photos de banques d'images libres de droits, comme Unsplash, avec le nom du photographe indiqué dans l'article, et d'éléments graphiques qui nous sont propres. Nous n'utilisons ni affiches, ni jaquettes, ni images protégées de films, de jeux ou de personnages. La vidéo d'un article, lorsqu'il y en a une, est un contenu officiel intégré depuis la chaîne où elle a été publiée, avec le nom de la chaîne. Si vous êtes l'auteur ou le propriétaire d'une image et souhaitez une autre mention ou son retrait, écrivez-nous.</p>
<h2>Corrections</h2>
<p>Lorsque nous trouvons une erreur, nous corrigeons l'article et signalons la correction dans le texte. Nous mettons aussi à jour les articles lorsque des dates ou des faits changent, afin que le contenu ne devienne pas obsolète. Si vous avez trouvé une erreur, envoyez l'article et ce qui est incorrect via la <a href="contato.html">page de contact</a>. Nous répondons dès que possible.</p>
<h2>Indépendance</h2>
<p>Notre contenu éditorial est indépendant. Les publicités, lorsqu'il y en a, sont séparées du texte et n'influencent pas ce que nous publions. Si un article implique un parrainage ou un partenariat, nous le dirons clairement.</p>
<h2>Traductions</h2>
<p>Le portugais est notre langue d'origine. Les éditions dans les autres langues sont adaptées par notre équipe, et non traduites mot à mot, et peuvent omettre des détails qui n'intéressent que le public brésilien. En cas de différence entre les versions, l'original en portugais fait foi.</p>""")
PAG["equipe.html"] = ("Équipe Aloha", "Qui signe les articles d'ALOHA NOTÍCIAS et ce que nous couvrons.", """
<p>Équipe Aloha est la signature de la rédaction d'ALOHA NOTÍCIAS. Elle réunit les personnes qui enquêtent, écrivent, réalisent les couvertures et relisent ce qui est publié ici.</p>
<h2>Qui est derrière le site</h2>
<p>ALOHA NOTÍCIAS est un projet éditorial indépendant, mené par une équipe et sans lien avec des studios, des producteurs ou des fabricants. Chaque article est relu et approuvé par une personne avant sa mise en ligne.</p>
<h2>À quoi vous attendre</h2>
<p>Des informations vérifiées auprès de plusieurs sources, des sources citées à la fin de chaque texte, des rumeurs signalées comme telles et des corrections faites au grand jour. Si quelque chose est faux, nous voulons le savoir.</p>
<h2>Ce que nous couvrons</h2>
<ul>@@EDITORIAS@@</ul>
<h2>Notre façon de travailler</h2>
<p>Nous confirmons les faits auprès de plusieurs sources, citons nos sources à la fin de chaque article et corrigeons les erreurs ouvertement. Consultez la <a href="politica-editorial.html">politique éditoriale</a>.</p>
<h2>Nous contacter</h2>
<p>Pistes de sujets, corrections et partenariats : <a href="contato.html">page de contact</a>.</p>""")
PAG["contato.html"] = ("Contact et publicité", "Contactez la rédaction d'ALOHA NOTÍCIAS.", """
<p>Écrivez-nous à <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Pour aller plus vite, indiquez le motif dans l'objet. Nous lisons le français, l'anglais, l'espagnol et le portugais.</p>
<h2>Propositions de sujets</h2><p>Vous avez vu quelque chose qui mérite un article ? Envoyez le sujet et, si possible, le lien vers la source.</p>
<h2>Corrections</h2><p>Vous avez trouvé une erreur ? Envoyez l'adresse de l'article et ce qui est incorrect, avec une source si possible. Voyez comment nous traitons les corrections dans la <a href="politica-editorial.html">politique éditoriale</a>.</p>
<h2>Droits d'auteur et images</h2><p>Si vous êtes l'auteur ou le propriétaire d'une image, d'un texte ou d'une vidéo et souhaitez corriger la mention ou demander le retrait, écrivez-nous avec l'adresse de la page et une preuve de propriété.</p>
<h2>Publicité et partenariats</h2><p>Pour faire de la publicité ou proposer un partenariat, écrivez à la même adresse. Le contenu sponsorisé sera toujours identifié comme tel.</p>
<h2>Confidentialité</h2><p>Les demandes concernant les données personnelles suivent ce qui est indiqué dans la <a href="privacidade.html">politique de confidentialité</a>.</p>""")
PAG["termos.html"] = ("Conditions d'utilisation", "Conditions d'utilisation du site ALOHA NOTÍCIAS.", """
<p>Dernière mise à jour : novembre 2026. En utilisant ALOHA NOTÍCIAS (alohanoticias.com), vous acceptez ces conditions. Si vous n'êtes pas d'accord, merci de ne pas utiliser le site.</p>
<h2>Ce qu'est le site</h2>
<p>ALOHA NOTÍCIAS publie des articles sur le cinéma, les jeux vidéo, la technologie, l'actualité et les curiosités. Le contenu est proposé à titre d'information et de divertissement.</p>
<h2>De l'information, pas des conseils</h2>
<p>Les articles sont informatifs et ne remplacent pas l'avis d'un professionnel. Nous faisons de notre mieux pour publier des informations exactes et à jour, mais les données, les prix et les dates peuvent changer après la publication.</p>
<h2>Propriété intellectuelle</h2>
<p>Les textes et illustrations originaux du site appartiennent à ALOHA NOTÍCIAS. Vous pouvez partager des liens et citer de courts extraits en indiquant la source et un lien vers l'article original. Il est interdit de copier des articles entiers, de les republier ou de les utiliser pour entraîner des systèmes automatisés sans autorisation écrite.</p>
<p>Les marques, noms, images et vidéos de tiers cités dans les articles appartiennent à leurs propriétaires et apparaissent à titre informatif, avec mention de la source. Si vous êtes propriétaire d'un contenu et souhaitez corriger la mention ou demander son retrait, contactez-nous via la <a href="contato.html">page de contact</a>.</p>
<h2>Liens et services tiers</h2>
<p>Le site peut contenir des liens vers d'autres sites et intégrer du contenu de services comme YouTube. Nous ne contrôlons pas ces adresses et ne sommes pas responsables de ce qu'elles publient ni de leurs règles.</p>
<h2>Publicité</h2>
<p>Le site peut afficher des publicités. Le cas échéant, elles seront identifiées comme telles et séparées du contenu éditorial. La présence d'une publicité ne signifie pas que nous recommandons le produit ou le service annoncé.</p>
<h2>Utilisation acceptable</h2>
<p>Vous vous engagez à ne pas tenter de nuire au fonctionnement du site, d'accéder à des zones restreintes, d'envoyer du code malveillant ni d'utiliser le site à des fins illégales.</p>
<h2>Limitation de responsabilité</h2>
<p>Le site est fourni tel quel. Nous ne garantissons pas qu'il sera toujours disponible ni exempt d'erreurs, et nous ne sommes pas responsables des pertes résultant de l'utilisation des informations publiées, dans les limites permises par la loi.</p>
<h2>Confidentialité</h2>
<p>Le traitement des données est décrit dans la <a href="privacidade.html">politique de confidentialité</a>.</p>
<h2>Modifications et droit applicable</h2>
<p>Nous pouvons modifier ces conditions ; la version en vigueur est celle publiée sur cette page, avec sa date de mise à jour. Ces conditions sont régies par le droit brésilien. En cas de différence, la version portugaise prévaut.</p>
<h2>Contact</h2>
<p>Questions sur ces conditions : <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>""")
PAG["privacidade.html"] = ("Confidentialité", "Politique de confidentialité d'ALOHA NOTÍCIAS.", """
<p>Dernière mise à jour : novembre 2026. Nous respectons la loi brésilienne générale sur la protection des données (LGPD, loi 13.709/2018). Voici, simplement, ce qu'il advient de vos données lorsque vous visitez ce site.</p>
<h2>Ce que nous collectons</h2>
<p>Nous ne demandons pas d'inscription et n'utilisons pas de cookies publicitaires ni de suivi. Nous enregistrons uniquement, dans votre propre navigateur, votre préférence de thème clair ou sombre.</p>
<p>Nous mesurons les visites avec Google Analytics, qui utilise des cookies de mesure d’audience pour compter les visites, les pages lues et la provenance des visiteurs (par exemple une recherche ou notre chaîne Telegram). Nous n’utilisons pas ces données pour vous identifier personnellement. Vous pouvez refuser dans l’avis sur les cookies ou via « Préférences de cookies » en bas de page ; les visiteurs de l’Union européenne, du Royaume-Uni et de la Suisse ne sont mesurés qu’après avoir accepté.</p>
<h2>Services tiers</h2>
<p>Les polices proviennent de Google Fonts. Les photos peuvent provenir d'Unsplash et les vidéos sont intégrées depuis YouTube en mode de confidentialité renforcée (youtube-nocookie.com). Lorsque ces éléments se chargent, ces services reçoivent votre adresse IP et peuvent avoir leurs propres règles de confidentialité. Le site est hébergé par Cloudflare.</p>
@@ANUNCIOS@@<h2>E-mail de contact</h2>
<p>Si vous nous écrivez, nous utilisons votre adresse e-mail uniquement pour répondre. Nous ne vendons ni ne partageons vos données.</p>
<h2>Vos droits</h2>
<p>Vous pouvez demander des informations sur les données que nous détenons à votre sujet, ainsi que leur correction ou leur suppression, en écrivant via la <a href="contato.html">page de contact</a>.</p>
<h2>Modifications</h2>
<p>Si cette politique change, la date ci-dessus sera mise à jour. Si nous commençons à utiliser des cookies, des publicités ou une newsletter, nous l'indiquerons d'abord ici. En cas de différence, la version portugaise prévaut.</p>""")
