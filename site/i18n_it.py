"""Italiano: interfaccia e pagine istituzionali."""
NOME = "Italiano"
MES = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
DIA = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ED = {
    "games": ("Videogiochi", "Uscite, cultura gaming e gli studi dietro i giochi."),
    "cinema": ("Cinema e serie", "Anteprime, retroscena e tutto ciò che sta intorno alla proiezione."),
    "tecnologia": ("Tecnologia", "Strumenti, sicurezza digitale e tecnologia di tutti i giorni, senza gergo."),
    "anime": ("Anime", "Anime, manga e cultura otaku: novità della stagione, adattamenti e ciò che va per la maggiore."),
    "curiosidades": ("Curiosità", "Domande che tutti si sono posti, con risposte scientifiche."),
}
UI = {
    "Pular para o conteúdo": "Vai al contenuto",
    "Início": "Home",
    "Buscar": "Cerca",
    "Alternar tema": "Cambia tema",
    "Abrir menu": "Apri il menu",
    "Editorias": "Sezioni",
    "Idioma / Language": "Lingua",
    "Traduzir esta página / Translate": "Lingua",
    "Traduzir / Translate": "Lingua",
    "Traduzir / Translate:": "Lingua:",
    "página inicial": "pagina iniziale",
    "Cinema, games e tecnologia explicados com calma, de olho no que importa.": "Cinema, videogiochi e tecnologia spiegati con calma, con lo sguardo su ciò che conta.",
    "Institucional": "Sul sito",
    "Sobre nós": "Chi siamo",
    "Contato e anúncios": "Contatti e pubblicità",
    "Equipe Aloha": "Team Aloha",
    "Sobre o autor": "L'autore",
    "Política editorial": "Linea editoriale",
    "Termos de uso": "Termini di utilizzo",
    "Privacidade": "Privacy",
    "RSS": "RSS (portoghese)",
    "Ilustração": "Illustrazione",
    "min de leitura": "min di lettura",
    "min": "min",
    "Mais lidas": "Più letti",
    "Voltar às notícias anteriores de": "Torna agli articoli precedenti di",
    "Ver mais notícias de": "Altri articoli in",
    "Ver tudo em": "Vedi tutto in",
    "Mais em": "Altro in",
    "Ainda não publicamos matérias nesta editoria. Volte em breve.": "Non abbiamo ancora pubblicato nulla in questa sezione. Torna presto.",
    "Você está em": "Ti trovi in",
    "Por": "Di",
    "Compartilhe": "Condividi",
    "Copiar link": "Copia il link",
    "Leia também": "Leggi anche",
    "Atualizado em": "Aggiornato il",
    "Atualização:": "Aggiornamento:",
    "Compartilhar no": "Condividi su",
    "Assuntos": "Argomenti",
    "matéria": "articolo",
    "matérias": "articoli",
    "sobre este assunto.": "su questo argomento.",
    "Matérias da ALOHA NOTÍCIAS sobre": "Articoli di ALOHA NOTÍCIAS su",
    "Busque matérias da ALOHA NOTÍCIAS.": "Cerca tra gli articoli di ALOHA NOTÍCIAS.",
    "Buscar matérias": "Cerca articoli",
    "Ex.: GTA 6, Vingadores, Switch 2": "Es.: GTA 6, Avengers, Switch 2",
    "Página não encontrada": "Pagina non trovata",
    "Essa onda passou": "Quest'onda è passata",
    "A página que você procurou não existe ou mudou de endereço.": "La pagina che cercavi non esiste o ha cambiato indirizzo.",
    "Voltar para a página inicial": "Torna alla home",
    "ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia": "ALOHA NOTÍCIAS: notizie, cinema, videogiochi e tecnologia",
    "Notícias, cinema, games e tecnologia, explicados com calma.": "Notizie, cinema, videogiochi e tecnologia, spiegati con calma.",
    "Destaques": "In evidenza",
    "Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.": "Scrivi un argomento, per esempio: GTA 6, Marvel o cinema.",
    "Nada encontrado para": "Nessun risultato per",
    "Tente outra palavra.": "Prova un'altra parola.",
    "matéria encontrada": "articolo trovato",
    "matérias encontradas": "articoli trovati",
    "Link copiado": "Link copiato",
    "Copie o endereço na barra do navegador": "Copia l'indirizzo dalla barra del browser",
    "Aviso de cookies": "Avviso sui cookie",
    "Aceitar": "Accetta",
    "Recusar": "Rifiuta",
    "Leia esta página em português (idioma original)": "Leggi questa pagina in portoghese (lingua originale)",
    "Esta matéria foi escrita em português e adaptada para o inglês pela equipe.": "Questo articolo è stato scritto in portoghese e adattato in italiano.",
    "Esta página também existe em": "Questa pagina esiste anche in",
    "Original em português": "Originale in portoghese",
}
CONSENT = "Usiamo i cookie per mostrare pubblicità e mantenere il sito gratuito. Scegli tu: se non accetti, non carichiamo la pubblicità."
SABER = "Scopri di più"
PRIV = """<h2>Pubblicità e cookie</h2>
<p>Questo sito mostra annunci di Google AdSense. Con il tuo consenso, Google e i suoi partner possono usare cookie e identificatori del dispositivo per mostrare annunci e misurarne le prestazioni. Gli annunci vengono caricati solo dopo che hai fatto clic su &laquo;Accetta&raquo; nell'avviso sui cookie; se rifiuti, il sito continua a funzionare normalmente, senza pubblicità. Puoi cambiare idea in qualsiasi momento nelle <a href="#" id="reabrir-consent">preferenze sui cookie</a>.</p>
<p>Scopri come Google usa i dati dei siti partner su <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. Puoi anche gestire gli annunci personalizzati su <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.</p>
"""
PAG = {}
PAG["sobre.html"] = ("Chi siamo", "Chi c'è dietro ALOHA NOTÍCIAS.", """
<p>ALOHA NOTÍCIAS è un sito di notizie brasiliano per chi vuole capire cosa succede senza il rumore di fondo. Ci concentriamo su cinema, videogiochi e tecnologia: anteprime, uscite e temi del momento, con i fatti verificati.</p>
<p>Il sito è stato creato ed è diretto da <a href="equipe.html">João Gabriel</a>, creatore di siti web e di contenuti digitali.</p>
<p>Scriviamo prima in portoghese. Questa edizione italiana è adattata per i lettori fuori dal Brasile, perciò spieghiamo le date e i dettagli di uscita brasiliani dove servono.</p>
<h2>Come lavoriamo</h2>
<p>Ogni articolo cita le proprie fonti, distingue i fatti dalle opinioni e viene corretto apertamente quando sbagliamo. I dettagli sono nella nostra <a href="politica-editorial.html">linea editoriale</a>.</p>
<h2>Il nome</h2>
<p><em>Aloha</em> è il saluto hawaiano che significa anche affetto e rispetto. È così che vogliamo trattare chi ci legge.</p>
<h2>Contatti</h2>
<p>Suggerimenti, correzioni e collaborazioni nella <a href="contato.html">pagina dei contatti</a>.</p>""")
PAG["politica-editorial.html"] = ("Linea editoriale e correzioni", "Come ALOHA NOTÍCIAS ricerca, scrive, illustra e corregge i propri articoli.", """
<p>Questa pagina spiega, in parole semplici, come vengono realizzati i contenuti di ALOHA NOTÍCIAS. Se non rispettiamo qualcosa di quanto scritto, vogliamo saperlo.</p>
<h2>Come verifichiamo i fatti</h2>
<p>Cerchiamo di confermare ogni informazione importante in più di una fonte prima di pubblicare. Date, prezzi e numeri entrano nel testo solo se compaiono nelle fonti consultate, che elenchiamo alla fine di ogni articolo. Quando un'informazione proviene da una sola fonte o non è ancora confermata, lo diciamo nel testo.</p>
<h2>Come scegliamo gli argomenti</h2>
<p>Diamo priorità a ciò che è d'attualità e utile ai lettori: anteprime, uscite, date e novità di cinema, videogiochi e tecnologia. Non pubblichiamo solo per ripetere un comunicato stampa. In ogni articolo cerchiamo di riunire ciò che è confermato, di ordinare ciò che ancora non si sa e di mostrare da dove proviene ogni informazione.</p>
<h2>Voci e indiscrezioni</h2>
<p>Voci, indiscrezioni e informazioni dietro le quinte compaiono solo quando sono rilevanti, sempre indicate come non confermate e con la fonte citata. Non trattiamo una voce come un fatto.</p>
<h2>Revisione prima della pubblicazione</h2>
<p>Nessun articolo viene pubblicato senza la revisione e l'approvazione dell'editore, <a href="equipe.html">João Gabriel</a>.</p>
<h2>Uso dell'intelligenza artificiale</h2>
<p>Usiamo strumenti di intelligenza artificiale come supporto al lavoro: per cercare e organizzare le informazioni, preparare bozze e adattare gli articoli in altre lingue. Nessun testo viene pubblicato direttamente dallo strumento. Ogni articolo viene verificato con le fonti, rivisto e approvato da João Gabriel prima della pubblicazione, e lui risponde di ciò che compare sul sito.</p>
<h2>Immagini e video</h2>
<p>In copertina e nel testo usiamo immagini promozionali ufficiali dell'argomento stesso, fornite da studi, piattaforme, sviluppatori e produttori. Le foto di archivi liberi, come Wikimedia Commons, compaiono solo quando mostrano qualcosa di cui parla il testo. Ogni immagine ha una didascalia con il credito di chi l'ha realizzata e, quando c'è, la licenza. Non usiamo immagini con filigrane di terzi. Il video di un articolo, quando c'è, è un contenuto ufficiale incorporato dal canale in cui è stato pubblicato, con il nome del canale. Se sei l'autore o il proprietario di un'immagine e vuoi un altro credito o la rimozione, scrivici dalla <a href="contato.html">pagina dei contatti</a>.</p>
<h2>Correzioni</h2>
<p>Quando troviamo un errore, correggiamo l'articolo e segnaliamo la correzione nel testo. Aggiorniamo gli articoli anche quando date o fatti cambiano, perché il contenuto non diventi obsoleto. Se hai trovato un errore, invia l'articolo e ciò che è sbagliato tramite la <a href="contato.html">pagina dei contatti</a>. Rispondiamo il prima possibile.</p>
<h2>Indipendenza</h2>
<p>I nostri contenuti editoriali sono indipendenti. Gli annunci, quando ci sono, sono separati dal testo e non influenzano ciò che pubblichiamo. Se un articolo prevede una sponsorizzazione o una collaborazione, lo diremo chiaramente.</p>
<h2>Traduzioni</h2>
<p>Il portoghese è la nostra lingua originale. Le edizioni nelle altre lingue sono adattate, non tradotte parola per parola, e possono omettere dettagli che interessano solo il pubblico brasiliano. Se le versioni differiscono, prevale l'originale in portoghese.</p>""")
PAG["equipe.html"] = ('João Gabriel', 'Chi crea, scrive e dirige ALOHA NOTÍCIAS.', """
<p><strong>João Gabriel</strong> ha 21 anni, è brasiliano, creatore di siti web e creatore di contenuti digitali sulle piattaforme. Ha creato ALOHA NOTÍCIAS, dove firma analisi, guide e articoli su videogiochi, cinema e cultura pop.</p>
<h2>Il sito</h2>
<p>ALOHA NOTÍCIAS è un progetto indipendente su cinema, videogiochi e tecnologia, senza legami con studi, produttori o fabbricanti.</p>
<h2>Cosa aspettarsi</h2>
<p>Informazioni verificate in più di una fonte, fonti citate alla fine di ogni testo, voci di corridoio indicate come tali e correzioni fatte apertamente. Se qualcosa è sbagliato, voglio saperlo. I dettagli sono nella <a href="politica-editorial.html">linea editoriale</a>.</p>
<h2>Di cosa ci occupiamo</h2>
<ul>@@EDITORIAS@@</ul>
<h2>Contatti</h2>
<p>Segnalazioni, correzioni e collaborazioni: <a href="contato.html">pagina dei contatti</a>.</p>""")
PAG["contato.html"] = ("Contatti e pubblicità", "Contatta ALOHA NOTÍCIAS.", """
<p>Scrivici a <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Per fare prima, indica il motivo nell'oggetto. Leggiamo italiano, inglese, spagnolo e portoghese.</p>
<h2>Suggerimenti di argomenti</h2><p>Hai visto qualcosa che merita un articolo? Invia l'argomento e, se ce l'hai, il link alla fonte.</p>
<h2>Correzioni</h2><p>Hai trovato un errore? Invia l'indirizzo dell'articolo e ciò che è sbagliato, possibilmente con una fonte. Vedi come gestiamo le correzioni nella <a href="politica-editorial.html">linea editoriale</a>.</p>
<h2>Diritto d'autore e immagini</h2><p>Se sei l'autore o il proprietario di un'immagine, di un testo o di un video e vuoi correggere il credito o chiederne la rimozione, scrivici con l'indirizzo della pagina e una prova di titolarità.</p>
<h2>Pubblicità e collaborazioni</h2><p>Per fare pubblicità o proporre una collaborazione, scrivi allo stesso indirizzo. I contenuti sponsorizzati saranno sempre indicati come tali.</p>
<h2>Privacy</h2><p>Le richieste sui dati personali seguono quanto indicato nell'<a href="privacidade.html">informativa sulla privacy</a>.</p>""")
PAG["termos.html"] = ("Termini di utilizzo", "Termini di utilizzo del sito ALOHA NOTÍCIAS.", """
<p>Ultimo aggiornamento: novembre 2026. Utilizzando ALOHA NOTÍCIAS (alohanoticias.com) accetti questi termini. Se non sei d'accordo, ti chiediamo di non utilizzare il sito.</p>
<h2>Cos'è il sito</h2>
<p>ALOHA NOTÍCIAS pubblica articoli su cinema, videogiochi, tecnologia, notizie e curiosità. I contenuti sono offerti a scopo informativo e di intrattenimento.</p>
<h2>Informazione, non consulenza</h2>
<p>Gli articoli sono informativi e non sostituiscono il parere di un professionista. Facciamo il possibile per pubblicare informazioni corrette e aggiornate, ma dati, prezzi e date possono cambiare dopo la pubblicazione.</p>
<h2>Proprietà intellettuale</h2>
<p>I testi e le illustrazioni originali del sito appartengono a ALOHA NOTÍCIAS. Puoi condividere link e citare brevi estratti con il credito e un link all'articolo originale. Non è consentito copiare articoli interi, ripubblicarli o usarli per addestrare sistemi automatici senza autorizzazione scritta.</p>
<p>Marchi, nomi, immagini e video di terzi citati negli articoli appartengono ai rispettivi proprietari e compaiono a scopo informativo, con il credito. Se sei proprietario di un contenuto e vuoi correggere il credito o chiederne la rimozione, contattaci tramite la <a href="contato.html">pagina dei contatti</a>.</p>
<h2>Link e servizi di terzi</h2>
<p>Il sito può contenere link ad altri siti e incorporare contenuti di servizi come YouTube. Non controlliamo questi indirizzi e non siamo responsabili di ciò che pubblicano né delle loro regole.</p>
<h2>Pubblicità</h2>
<p>Il sito può mostrare annunci. Quando ci sono, saranno identificati come pubblicità e separati dai contenuti editoriali. La presenza di un annuncio non significa che approviamo il prodotto o il servizio pubblicizzato.</p>
<h2>Uso consentito</h2>
<p>Ti impegni a non cercare di compromettere il funzionamento del sito, ad accedere ad aree riservate, a inviare codice dannoso né a usare il sito per scopi illeciti.</p>
<h2>Limitazione di responsabilità</h2>
<p>Il sito è fornito così com'è. Non garantiamo che sia sempre disponibile o privo di errori e, nei limiti consentiti dalla legge, non siamo responsabili di perdite derivanti dall'uso delle informazioni pubblicate.</p>
<h2>Privacy</h2>
<p>Il trattamento dei dati è descritto nell'<a href="privacidade.html">informativa sulla privacy</a>.</p>
<h2>Modifiche e legge applicabile</h2>
<p>Possiamo modificare questi termini; la versione in vigore è quella pubblicata in questa pagina, con la data di aggiornamento. Questi termini sono regolati dalla legge brasiliana. In caso di differenze prevale la versione in portoghese.</p>
<h2>Contatti</h2>
<p>Domande su questi termini: <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>""")
PAG["privacidade.html"] = ("Privacy", "Informativa sulla privacy di ALOHA NOTÍCIAS.", """
<p>Ultimo aggiornamento: novembre 2026. Rispettiamo la legge brasiliana sulla protezione dei dati (LGPD, legge 13.709/2018). Ecco, in parole semplici, cosa succede ai tuoi dati quando visiti questo sito.</p>
<h2>Cosa raccogliamo</h2>
<p>Non chiediamo registrazione e non usiamo cookie pubblicitari né di tracciamento. Salviamo solo, nel tuo browser, la tua preferenza per il tema chiaro o scuro.</p>
<p>Misuriamo le visite con Google Analytics, che usa cookie statistici per contare gli accessi, le pagine lette e da dove arrivano le visite (per esempio da una ricerca o dal nostro canale Telegram). Non usiamo questi dati per identificarti personalmente. Puoi rifiutare nell’avviso sui cookie o in “Preferenze cookie” a piè di pagina; i visitatori dell’Unione europea, del Regno Unito e della Svizzera vengono misurati solo dopo aver accettato.</p>
<h2>Servizi di terzi</h2>
<p>I caratteri provengono da Google Fonts. Le foto possono provenire da Unsplash e i video sono incorporati da YouTube in modalità di privacy avanzata (youtube-nocookie.com). Quando questi elementi vengono caricati, i relativi servizi ricevono il tuo indirizzo IP e possono avere proprie regole sulla privacy. Il sito è ospitato da Cloudflare.</p>
@@ANUNCIOS@@<h2>E-mail di contatto</h2>
<p>Se ci scrivi, useremo la tua e-mail solo per rispondere. Non vendiamo né condividiamo i tuoi dati.</p>
<h2>I tuoi diritti</h2>
<p>Puoi chiedere informazioni sui dati che abbiamo su di te, la loro correzione o cancellazione, scrivendo tramite la <a href="contato.html">pagina dei contatti</a>.</p>
<h2>Modifiche</h2>
<p>Se questa informativa cambia, la data qui sopra sarà aggiornata. Se inizieremo a usare cookie, pubblicità o una newsletter, lo diremo prima qui. In caso di differenze prevale la versione in portoghese.</p>""")

PAG["equipe-aloha.html"] = ('Team Aloha', 'Chi firma come Team Aloha su ALOHA NOTÍCIAS.', """
<p><strong>Team Aloha</strong> è la firma della redazione di ALOHA NOTÍCIAS, usata in parte degli articoli su cinema, videogiochi, tecnologia, anime e curiosità.</p>
<h2>Come nascono questi articoli</h2>
<p>Seguono la stessa <a href="politica-editorial.html">linea editoriale</a> del resto del sito. Sono ricercati e scritti con il supporto di strumenti, come spiega la linea editoriale, e ogni articolo viene rivisto e approvato da una persona prima della pubblicazione.</p>""")
