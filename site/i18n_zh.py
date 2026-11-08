"""简体中文：界面与说明页面。"""
NOME = "中文"
MES = [f"{i}月" for i in range(1, 13)]
DIA = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
ED = {
    "games": ("游戏", "新作发售、游戏文化，以及游戏背后的工作室。"),
    "cinema": ("影视", "上映资讯、幕后故事，以及观影前后你想知道的一切。"),
    "tecnologia": ("科技", "工具、数字安全和日常科技，不堆术语。"),
    "anime": ("动漫", "动漫、漫画与宅文化：当季新番、改编消息和当下热点。"),
    "curiosidades": ("冷知识", "人人都好奇的问题，用科学来回答。"),
}
UI = {
    "Pular para o conteúdo": "跳到正文",
    "Início": "首页",
    "Buscar": "搜索",
    "Alternar tema": "切换主题",
    "Abrir menu": "打开菜单",
    "Editorias": "栏目",
    "Idioma / Language": "语言",
    "Traduzir esta página / Translate": "语言",
    "Traduzir / Translate": "语言",
    "Traduzir / Translate:": "语言：",
    "página inicial": "首页",
    "Cinema, games e tecnologia explicados com calma, de olho no que importa.": "影视、游戏与科技，从容讲述，只关注真正重要的事。",
    "Institucional": "关于本站",
    "Sobre nós": "关于我们",
    "Contato e anúncios": "联系我们与广告合作",
    "Equipe Aloha": "Aloha 编辑部",
    "Política editorial": "编辑方针",
    "Termos de uso": "使用条款",
    "Privacidade": "隐私政策",
    "RSS": "RSS（葡萄牙语）",
    "Ilustração": "插图",
    "min de leitura": "分钟阅读",
    "min": "分钟",
    "Mais lidas": "热门文章",
    "Voltar às notícias anteriores de": "返回更早的文章：",
    "Ver mais notícias de": "更多文章：",
    "Ver tudo em": "查看全部：",
    "Mais em": "更多：",
    "Ainda não publicamos matérias nesta editoria. Volte em breve.": "这个栏目还没有文章，敬请期待。",
    "Você está em": "当前位置",
    "Por": "作者：",
    "Compartilhe": "分享",
    "Copiar link": "复制链接",
    "Leia também": "延伸阅读",
    "Atualizado em": "更新于",
    "Atualização:": "更新：",
    "Compartilhar no": "分享到",
    "Assuntos": "相关话题",
    "matéria": "篇文章",
    "matérias": "篇文章",
    "sobre este assunto.": "与此话题相关的文章。",
    "Matérias da ALOHA NOTÍCIAS sobre": "ALOHA NOTÍCIAS 上关于以下话题的文章：",
    "Busque matérias da ALOHA NOTÍCIAS.": "搜索 ALOHA NOTÍCIAS 的文章。",
    "Buscar matérias": "搜索文章",
    "Ex.: GTA 6, Vingadores, Switch 2": "例如：GTA 6、复仇者联盟、Switch 2",
    "Página não encontrada": "页面不存在",
    "Essa onda passou": "这道浪已经过去了",
    "A página que você procurou não existe ou mudou de endereço.": "你要找的页面不存在，或者地址已经变更。",
    "Voltar para a página inicial": "返回首页",
    "ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia": "ALOHA NOTÍCIAS：新闻、影视、游戏与科技",
    "Notícias, cinema, games e tecnologia, explicados com calma.": "新闻、影视、游戏与科技，从容讲述。",
    "Destaques": "头条",
    "Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.": "输入关键词，例如：GTA 6、漫威或电影。",
    "Nada encontrado para": "没有找到相关内容：",
    "Tente outra palavra.": "换个关键词试试。",
    "matéria encontrada": "篇相关文章",
    "matérias encontradas": "篇相关文章",
    "Link copiado": "链接已复制",
    "Copie o endereço na barra do navegador": "请从浏览器地址栏复制网址",
    "Aviso de cookies": "Cookie 提示",
    "Aceitar": "接受",
    "Recusar": "拒绝",
    "Leia esta página em português (idioma original)": "阅读葡萄牙语原文页面",
    "Esta matéria foi escrita em português e adaptada para o inglês pela equipe.": "本文原以葡萄牙语写成，由编辑部针对中文读者改写。",
    "Esta página também existe em": "本页还有以下语言版本：",
    "Original em português": "葡萄牙语原文",
}
CONSENT = "我们使用 Cookie 来展示广告，让网站保持免费。是否接受由你决定：如果不接受，我们就不会加载广告。"
SABER = "了解更多"
PRIV = """<h2>广告与 Cookie</h2>
<p>本站展示 Google AdSense 广告。经你许可，Google 及其合作伙伴可能使用 Cookie 和设备标识符来展示广告并衡量广告效果。只有在你点击 Cookie 提示中的“接受”之后，广告才会加载；如果你拒绝，网站仍可正常使用，只是不显示广告。你可以随时在 <a href="#" id="reabrir-consent">Cookie 偏好设置</a>中改变主意。</p>
<p>想了解 Google 如何使用合作网站的数据，请访问 <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>。你也可以在 <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a> 管理个性化广告。</p>
"""
PAG = {}
PAG["sobre.html"] = ("关于我们", "ALOHA NOTÍCIAS 背后是谁。", """
<p>ALOHA NOTÍCIAS 是一个巴西新闻网站，写给那些想弄明白正在发生什么、又不想被噪音淹没的人。我们重点关注影视、游戏和科技：上映、发售和正在热议的话题，并且核实过事实。</p>
<p>我们的文章首先用葡萄牙语写成。这个中文版由编辑部为巴西以外的读者改写，所以凡是涉及巴西的日期和上映信息，我们会在需要的地方补充说明。</p>
<h2>我们怎么工作</h2>
<p>每篇文章都会列出信息来源，区分事实与观点，出错时公开更正。详情见我们的<a href="politica-editorial.html">编辑方针</a>。</p>
<h2>名字的由来</h2>
<p><em>Aloha</em>（阿罗哈）是夏威夷的问候语，也有关爱与尊重的意思。我们希望用这样的态度对待每一位读者。</p>
<h2>联系我们</h2>
<p>建议、更正和合作，请通过<a href="contato.html">联系页面</a>告诉我们。</p>""")
PAG["politica-editorial.html"] = ("编辑方针与更正政策", "ALOHA NOTÍCIAS 如何采访、写作、配图和更正文章。", """
<p>本页用通俗的话说明 ALOHA NOTÍCIAS 的内容是怎么做出来的。如果我们没有做到其中任何一条，请告诉我们。</p>
<h2>我们如何核实事实</h2>
<p>发布之前，我们会尽量用不止一个来源确认每条重要信息。日期、价格和数字，只有出现在我们查阅过的来源中才会写进正文，这些来源会列在每篇文章的末尾。如果某条信息只有单一来源，或者尚未得到证实，我们会在文中直接说明。</p>
<h2>我们如何选题</h2>
<p>我们优先选择正在热议、对读者有用的内容：影视、游戏和科技领域的上映、发售、日期和新动态。我们不会为了转述一份新闻稿而发文。在每篇文章里，我们会尽力把已经确认的内容汇总起来，把尚不清楚的部分理清楚，并标明每条信息的出处。</p>
<h2>传闻与爆料</h2>
<p>传闻、爆料和幕后消息，只有在有意义时才会出现，而且一律标明未经证实，并写明来源。我们不会把传闻当作事实。</p>
<h2>发布前审核</h2>
<p>没有经过编辑部成员审核和批准的文章，不会上线。</p>
<h2>图片与视频</h2>
<p>我们的封面由编辑部用 Unsplash 等可自由使用的图库照片拼合而成，文章中会标注摄影师，并配有我们自己的图形元素。我们不使用电影、游戏或角色的海报、封面和受保护的图片。文章中的视频（如有）是从原发布频道嵌入的官方内容，并标明频道名称。如果你是某张图片的作者或权利人，希望更改署名或删除，请联系我们。</p>
<h2>更正</h2>
<p>发现错误时，我们会修改文章，并在文中标明更正。当日期或事实发生变化时，我们也会更新文章，避免内容过时。如果你发现了错误，请通过<a href="contato.html">联系页面</a>发来文章和错误之处。我们会尽快回复。</p>
<h2>独立性</h2>
<p>我们的编辑内容是独立的。广告（如果有）与正文分开，不会影响我们发布什么。如果某篇文章涉及赞助或合作，我们会明确说明。</p>
<h2>关于翻译</h2>
<p>葡萄牙语是我们的原文语言。其他语言版本由编辑部改写，而不是逐字翻译，可能会省去只对巴西读者有意义的细节。如果各版本之间存在差异，以葡萄牙语原文为准。</p>""")
PAG["equipe.html"] = ("Aloha 编辑部", "谁在署名 ALOHA NOTÍCIAS 的文章，以及我们的报道范围。", """
<p>Aloha 编辑部是 ALOHA NOTÍCIAS 编辑团队的统一署名，汇集了在这里采访、写作、制作封面并审核发布内容的人。</p>
<h2>幕后是谁</h2>
<p>ALOHA NOTÍCIAS 是一个由团队运营的独立编辑项目，与制片公司、发行方和厂商没有任何关联。每篇文章在上线前都由一位成员审核并批准。</p>
<h2>你可以期待什么</h2>
<p>多个来源核实过的信息，每篇文章末尾列出的来源，明确标注为传闻的传闻，以及公开进行的更正。如果有错误，我们想知道。</p>
<h2>我们报道什么</h2>
<ul>@@EDITORIAS@@</ul>
<h2>我们怎么工作</h2>
<p>我们用不止一个来源确认事实，在每篇文章末尾列出来源，并公开更正错误。请参阅<a href="politica-editorial.html">编辑方针</a>。</p>
<h2>联系我们</h2>
<p>线索、更正和合作：<a href="contato.html">联系页面</a>。</p>""")
PAG["contato.html"] = ("联系我们与广告合作", "联系 ALOHA NOTÍCIAS 编辑部。", """
<p>请发邮件至 <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>。为了更快处理，请在邮件主题里写明来意。我们能阅读中文、英语、西班牙语和葡萄牙语的来信。</p>
<h2>选题线索</h2><p>看到值得写成文章的事？请发来主题，如果有的话，附上来源链接。</p>
<h2>更正</h2><p>发现错误？请发来文章地址和错误之处，最好附上来源。我们如何处理更正，见<a href="politica-editorial.html">编辑方针</a>。</p>
<h2>版权与图片</h2><p>如果你是某张图片、某段文字或某个视频的作者或权利人，希望更正署名或要求删除，请发来页面地址和权属证明。</p>
<h2>广告与合作</h2><p>想投放广告或提出合作，请发到同一个邮箱。赞助内容一定会标明。</p>
<h2>隐私</h2><p>关于个人数据的请求，按<a href="privacidade.html">隐私政策</a>中的说明处理。</p>""")
PAG["termos.html"] = ("使用条款", "ALOHA NOTÍCIAS 网站的使用条款。", """
<p>最后更新：2026 年 11 月。使用 ALOHA NOTÍCIAS（alohanoticias.com），即表示你同意本条款。如果你不同意，请不要使用本站。</p>
<h2>本站是什么</h2>
<p>ALOHA NOTÍCIAS 发布关于影视、游戏、科技、新闻和冷知识的文章。内容仅供信息参考和娱乐。</p>
<h2>提供信息，而非建议</h2>
<p>文章仅供参考，不能替代专业人士的意见。我们会尽力发布准确、及时的信息，但数据、价格和日期在发布后可能发生变化。</p>
<h2>知识产权</h2>
<p>本站的原创文字和插图归 ALOHA NOTÍCIAS 所有。你可以分享链接，也可以引用简短片段，但需注明出处并附上原文链接。未经书面许可，不得复制整篇文章、转载，或将其用于训练自动化系统。</p>
<p>文章中提到的第三方商标、名称、图片和视频归各自所有者所有，仅用于信息说明，并标注来源。如果你是某项内容的所有者，希望更正署名或要求删除，请通过<a href="contato.html">联系页面</a>与我们联系。</p>
<h2>链接与第三方服务</h2>
<p>本站可能链接到其他网站，也可能嵌入 YouTube 等服务的内容。我们无法控制这些地址，对其发布的内容和规则不承担责任。</p>
<h2>广告</h2>
<p>本站可能展示广告。展示时会标明是广告，并与编辑内容分开。出现广告并不意味着我们认可所宣传的产品或服务。</p>
<h2>合理使用</h2>
<p>你同意不会试图妨碍本站运行、访问受限区域、发送恶意代码，或将本站用于违法目的。</p>
<h2>责任限制</h2>
<p>本站按现状提供。我们不保证它始终可用或没有错误，并在法律允许的范围内，对因使用所发布信息而造成的损失不承担责任。</p>
<h2>隐私</h2>
<p>数据处理方式见<a href="privacidade.html">隐私政策</a>。</p>
<h2>变更与适用法律</h2>
<p>我们可能修改本条款，有效版本以本页发布的版本及其更新日期为准。本条款适用巴西法律。如有差异，以葡萄牙语版本为准。</p>
<h2>联系方式</h2>
<p>对本条款有疑问：<a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>。</p>""")
PAG["privacidade.html"] = ("隐私政策", "ALOHA NOTÍCIAS 的隐私政策。", """
<p>最后更新：2026 年 11 月。我们遵守巴西《通用数据保护法》（LGPD，第 13.709/2018 号法律）。下面用直白的话说明：你访问本站时，你的数据会怎样处理。</p>
<h2>我们收集什么</h2>
<p>我们不要求注册，也不使用广告或追踪类 Cookie。我们只会在你自己的浏览器中保存你选择的浅色或深色主题。</p>
<p>我们使用 Google Analytics 统计访问，它通过统计 Cookie 计算访问量、阅读的页面以及访问来源（例如搜索或我们的 Telegram 频道）。我们不会用这些数据识别您的个人身份。您可以在 Cookie 提示或页脚的“Cookie 偏好设置”中拒绝；来自欧盟、英国和瑞士的访客只有在同意后才会被统计。</p>
<h2>第三方服务</h2>
<p>字体来自 Google Fonts。照片可能来自 Unsplash，视频以增强隐私模式（youtube-nocookie.com）从 YouTube 嵌入。这些内容加载时，相关服务会获取你的 IP 地址，并可能有各自的隐私规则。本站托管在 Cloudflare 上。</p>
@@ANUNCIOS@@<h2>联系邮箱</h2>
<p>如果你给我们写信，我们只会用你的邮箱来回复。我们不会出售或分享你的数据。</p>
<h2>你的权利</h2>
<p>你可以通过<a href="contato.html">联系页面</a>写信，要求了解我们持有的你的数据，并要求更正或删除。</p>
<h2>变更</h2>
<p>如果本政策有变化，上方的日期会随之更新。如果我们开始使用 Cookie、广告或新闻邮件，会先在这里说明。如有差异，以葡萄牙语版本为准。</p>""")
