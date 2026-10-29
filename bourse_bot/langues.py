"""Version 47 : le radar dans les grandes langues du monde (pages statiques).

Pour chaque langue : une page d'accueil et une page par titre, avec les chiffres du jour (cours, agitation prévue,
risque de forte chute, avis des IA quand il a fait ses preuves). Chaque page est reliée à ses jumelles dans
toutes les autres langues (balises hreflang) : Google montre à chaque visiteur la version dans sa langue.
L'application interactive reste en français ; l'anglais a ses propres pages plus complètes (anglais.py).
"""
from __future__ import annotations

import html
import math
import os
import re

from . import seo

NOM = seo.NOM

# code : (nom de la langue dans la langue, locale og, sens d'écriture, séparateur décimal)
LANGUES = {
    "es": ("Español", "es_ES", "ltr", ","),
    "de": ("Deutsch", "de_DE", "ltr", ","),
    "it": ("Italiano", "it_IT", "ltr", ","),
    "pt": ("Português", "pt_BR", "ltr", ","),
    "nl": ("Nederlands", "nl_NL", "ltr", ","),
    "ru": ("Русский", "ru_RU", "ltr", ","),
    "tr": ("Türkçe", "tr_TR", "ltr", ","),
    "ar": ("العربية", "ar_AR", "rtl", "."),
    "hi": ("हिन्दी", "hi_IN", "ltr", "."),
    "zh": ("中文", "zh_CN", "ltr", "."),
    "ja": ("日本語", "ja_JP", "ltr", "."),
    "ko": ("한국어", "ko_KR", "ltr", "."),
}
TOUTES = ["fr", "en"] + list(LANGUES)
NOMS_LANGUES = {"fr": "Français", "en": "English", **{k: v[0] for k, v in LANGUES.items()}}

# Textes. {nom} = nom du titre, {tk} = symbole, {n} = nombre, {h} = horizon en séances.
AGIT_SEMAINE = {'es': 'movimiento previsto en 5 sesiones', 'de': 'erwartete Bewegung in 5 Handelstagen', 'it': 'movimento previsto in 5 sedute', 'pt': 'movimento previsto em 5 pregões', 'nl': 'verwachte beweging in 5 handelsdagen', 'ru': 'ожидаемое движение за 5 торговых дней', 'tr': '5 işlem gününde beklenen hareket', 'ar': 'الحركة المتوقعة خلال 5 جلسات', 'hi': '5 सत्रों में अनुमानित उतार-चढ़ाव', 'zh': '未来 5 个交易日预计波动', 'ja': '今後5営業日の予想変動', 'ko': '향후 5거래일 예상 변동 폭'}

T = {
 "es": dict(
   titre_page="{nom} ({tk}): previsión y análisis a un mes", h1="{nom} ({tk}): previsión a un mes",
   desc="{nom} ({tk}): cotización, movimiento previsto, riesgo de caída fuerte y opinión de las IA, actualizado cada día. Proyecto educativo gratuito, no es un consejo.",
   maj="Actualizado automáticamente · precios del {d}", prix="último precio", perf="en 1 mes",
   agit="movimiento previsto en un mes", chute="riesgo de caer más de un 10 %", sens="probabilidad de estar más alto en {h} sesiones",
   sans_avis="sin opinión clara", sur10="{n} de 10",
   fiable_t="¿Qué es fiable?", fiable=("Adivinar si el precio subirá o bajará en un mes es casi imposible: probadas en años que nunca habían visto, "
     "nuestras IA no lo hacen mejor que la regla «siempre sube». En cambio, prevén bien <b>cuánto</b> se moverá el precio y el <b>riesgo de una caída fuerte</b>."),
   app="Abrir la aplicación interactiva (en francés)", en="Versión en inglés",
   accueil_t="{nom}: previsiones gratuitas de acciones y criptomonedas", accueil_h1="{nom}: previsiones de bolsa y cripto, explicadas con sencillez",
   accueil_desc="Previsiones gratuitas a un mes para acciones francesas, europeas y estadounidenses, ETF y criptomonedas: movimiento previsto y riesgo de caída. Proyecto educativo.",
   accueil_intro="Más de 200 acciones, ETF y criptomonedas analizados automáticamente cada hora. Gratis, sin registro, educativo.",
   risque_t="Mayor riesgo de caída fuerte este mes", calmes_t="Los más tranquilos previstos este mes", tous="Todas las acciones y criptomonedas",
   avert="<b>Nada es seguro en bolsa.</b> {nom} es un proyecto educativo gratuito. Estas cifras se generan automáticamente, pueden contener errores y no son un consejo de inversión. Puedes perder todo el dinero invertido.",
   marches={"fr": "Acciones francesas", "eu": "Acciones europeas", "us": "Acciones de EE. UU.", "crypto": "Criptomonedas", "etf": "ETF e índices", "tendances": "Tendencias"},
   langues="Idiomas"),
 "de": dict(
   titre_page="{nom} ({tk}): Prognose und Analyse für einen Monat", h1="{nom} ({tk}): Prognose für einen Monat",
   desc="{nom} ({tk}): Kurs, erwartete Schwankung, Risiko eines starken Rückgangs und Einschätzung der KI, täglich aktualisiert. Kostenloses Bildungsprojekt, keine Anlageberatung.",
   maj="Automatisch aktualisiert · Kurse vom {d}", prix="letzter Kurs", perf="in 1 Monat",
   agit="erwartete Bewegung in einem Monat", chute="Risiko eines Rückgangs um mehr als 10 %", sens="Chance, in {h} Handelstagen höher zu stehen",
   sans_avis="keine klare Einschätzung", sur10="{n} von 10",
   fiable_t="Was ist verlässlich?", fiable=("Ob ein Kurs in einem Monat höher oder tiefer steht, lässt sich kaum vorhersagen: Getestet an Jahren, die sie nie gesehen hatten, "
     "sind unsere KIs nicht besser als die Regel „steigt immer“. Gut vorhersagen sie dagegen, <b>wie stark</b> sich der Kurs bewegt, und das <b>Risiko eines starken Rückgangs</b>."),
   app="Interaktive App öffnen (auf Französisch)", en="Englische Version",
   accueil_t="{nom}: kostenlose Prognosen für Aktien und Kryptowährungen", accueil_h1="{nom}: Börsen- und Krypto-Prognosen, einfach erklärt",
   accueil_desc="Kostenlose Ein-Monats-Prognosen für französische, europäische und US-Aktien, ETFs und Kryptowährungen: erwartete Schwankung und Rückgangsrisiko. Bildungsprojekt.",
   accueil_intro="Über 200 Aktien, ETFs und Kryptowährungen, stündlich automatisch analysiert. Kostenlos, ohne Anmeldung, zu Bildungszwecken.",
   risque_t="Höchstes Risiko eines starken Rückgangs in diesem Monat", calmes_t="Die ruhigsten Werte in diesem Monat", tous="Alle Aktien und Kryptowährungen",
   avert="<b>An der Börse ist nichts sicher.</b> {nom} ist ein kostenloses Bildungsprojekt. Diese Zahlen werden automatisch erstellt, können Fehler enthalten und sind keine Anlageberatung. Sie können Ihr gesamtes investiertes Geld verlieren.",
   marches={"fr": "Französische Aktien", "eu": "Europäische Aktien", "us": "US-Aktien", "crypto": "Kryptowährungen", "etf": "ETFs und Indizes", "tendances": "Im Trend"},
   langues="Sprachen"),
 "it": dict(
   titre_page="{nom} ({tk}): previsione e analisi a un mese", h1="{nom} ({tk}): previsione a un mese",
   desc="{nom} ({tk}): quotazione, movimento previsto, rischio di forte calo e parere delle IA, aggiornati ogni giorno. Progetto educativo gratuito, non è un consiglio.",
   maj="Aggiornato automaticamente · prezzi del {d}", prix="ultimo prezzo", perf="in 1 mese",
   agit="movimento previsto in un mese", chute="rischio di calare di oltre il 10 %", sens="probabilità di essere più alto tra {h} sedute",
   sans_avis="nessun parere netto", sur10="{n} su 10",
   fiable_t="Cosa è affidabile?", fiable=("Indovinare se il prezzo salirà o scenderà in un mese è quasi impossibile: testate su anni mai visti, "
     "le nostre IA non fanno meglio della regola «sale sempre». Prevedono bene invece <b>quanto</b> si muoverà il prezzo e il <b>rischio di un forte calo</b>."),
   app="Apri l'applicazione interattiva (in francese)", en="Versione inglese",
   accueil_t="{nom}: previsioni gratuite su azioni e criptovalute", accueil_h1="{nom}: previsioni di borsa e cripto, spiegate in modo semplice",
   accueil_desc="Previsioni gratuite a un mese per azioni francesi, europee e americane, ETF e criptovalute: movimento previsto e rischio di calo. Progetto educativo.",
   accueil_intro="Oltre 200 azioni, ETF e criptovalute analizzati automaticamente ogni ora. Gratis, senza registrazione, educativo.",
   risque_t="Rischio più alto di forte calo questo mese", calmes_t="I più tranquilli previsti questo mese", tous="Tutte le azioni e le criptovalute",
   avert="<b>In borsa nulla è certo.</b> {nom} è un progetto educativo gratuito. Questi dati sono generati automaticamente, possono contenere errori e non costituiscono un consiglio di investimento. Puoi perdere tutto il denaro investito.",
   marches={"fr": "Azioni francesi", "eu": "Azioni europee", "us": "Azioni USA", "crypto": "Criptovalute", "etf": "ETF e indici", "tendances": "Di tendenza"},
   langues="Lingue"),
 "pt": dict(
   titre_page="{nom} ({tk}): previsão e análise para um mês", h1="{nom} ({tk}): previsão para um mês",
   desc="{nom} ({tk}): cotação, movimento previsto, risco de queda forte e opinião das IAs, atualizados todos os dias. Projeto educativo gratuito, não é recomendação.",
   maj="Atualizado automaticamente · preços de {d}", prix="último preço", perf="em 1 mês",
   agit="movimento previsto em um mês", chute="risco de cair mais de 10 %", sens="chance de estar mais alto em {h} pregões",
   sans_avis="sem opinião clara", sur10="{n} em 10",
   fiable_t="O que é confiável?", fiable=("Adivinhar se o preço vai subir ou cair em um mês é quase impossível: testadas em anos que nunca tinham visto, "
     "nossas IAs não fazem melhor que a regra «sempre sobe». Por outro lado, preveem bem <b>quanto</b> o preço vai se mexer e o <b>risco de uma queda forte</b>."),
   app="Abrir o aplicativo interativo (em francês)", en="Versão em inglês",
   accueil_t="{nom}: previsões gratuitas de ações e criptomoedas", accueil_h1="{nom}: previsões de bolsa e cripto, explicadas de forma simples",
   accueil_desc="Previsões gratuitas de um mês para ações francesas, europeias e americanas, ETFs e criptomoedas: movimento previsto e risco de queda. Projeto educativo.",
   accueil_intro="Mais de 200 ações, ETFs e criptomoedas analisados automaticamente a cada hora. Grátis, sem cadastro, educativo.",
   risque_t="Maior risco de queda forte este mês", calmes_t="Os mais tranquilos previstos este mês", tous="Todas as ações e criptomoedas",
   avert="<b>Nada é garantido na bolsa.</b> {nom} é um projeto educativo gratuito. Estes números são gerados automaticamente, podem conter erros e não são recomendação de investimento. Você pode perder todo o dinheiro investido.",
   marches={"fr": "Ações francesas", "eu": "Ações europeias", "us": "Ações dos EUA", "crypto": "Criptomoedas", "etf": "ETFs e índices", "tendances": "Em alta"},
   langues="Idiomas"),
 "nl": dict(
   titre_page="{nom} ({tk}): verwachting en analyse voor een maand", h1="{nom} ({tk}): verwachting voor een maand",
   desc="{nom} ({tk}): koers, verwachte beweging, risico op een sterke daling en mening van de AI's, dagelijks bijgewerkt. Gratis educatief project, geen advies.",
   maj="Automatisch bijgewerkt · koersen van {d}", prix="laatste koers", perf="in 1 maand",
   agit="verwachte beweging in een maand", chute="risico op een daling van meer dan 10 %", sens="kans om over {h} handelsdagen hoger te staan",
   sans_avis="geen duidelijke mening", sur10="{n} op 10",
   fiable_t="Wat is betrouwbaar?", fiable=("Raden of een koers over een maand hoger of lager staat, is bijna onmogelijk: getest op jaren die ze nooit hadden gezien, "
     "doen onze AI's het niet beter dan de regel „stijgt altijd”. Ze voorspellen wel goed <b>hoeveel</b> de koers beweegt en het <b>risico op een sterke daling</b>."),
   app="Open de interactieve app (in het Frans)", en="Engelse versie",
   accueil_t="{nom}: gratis verwachtingen voor aandelen en crypto", accueil_h1="{nom}: beurs- en cryptoverwachtingen, eenvoudig uitgelegd",
   accueil_desc="Gratis verwachtingen voor een maand voor Franse, Europese en Amerikaanse aandelen, ETF's en crypto: verwachte beweging en dalingsrisico. Educatief project.",
   accueil_intro="Meer dan 200 aandelen, ETF's en cryptomunten, elk uur automatisch geanalyseerd. Gratis, zonder registratie, educatief.",
   risque_t="Hoogste risico op een sterke daling deze maand", calmes_t="De rustigste verwacht deze maand", tous="Alle aandelen en cryptomunten",
   avert="<b>Op de beurs is niets zeker.</b> {nom} is een gratis educatief project. Deze cijfers worden automatisch gemaakt, kunnen fouten bevatten en zijn geen beleggingsadvies. U kunt al het belegde geld verliezen.",
   marches={"fr": "Franse aandelen", "eu": "Europese aandelen", "us": "Amerikaanse aandelen", "crypto": "Cryptomunten", "etf": "ETF's en indices", "tendances": "Trending"},
   langues="Talen"),
 "ru": dict(
   titre_page="{nom} ({tk}): прогноз и анализ на месяц", h1="{nom} ({tk}): прогноз на месяц",
   desc="{nom} ({tk}): котировка, ожидаемое движение, риск сильного падения и мнение ИИ, обновляются ежедневно. Бесплатный образовательный проект, не инвестиционный совет.",
   maj="Обновляется автоматически · цены на {d}", prix="последняя цена", perf="за 1 месяц",
   agit="ожидаемое движение за месяц", chute="риск падения более чем на 10 %", sens="шанс оказаться выше через {h} торговых дней",
   sans_avis="нет чёткого мнения", sur10="{n} из 10",
   fiable_t="Чему можно доверять?", fiable=("Угадать, будет ли цена выше или ниже через месяц, почти невозможно: на годах, которых они не видели, "
     "наши ИИ справляются не лучше правила «всегда растёт». Зато они хорошо предсказывают, <b>насколько сильно</b> изменится цена, и <b>риск сильного падения</b>."),
   app="Открыть интерактивное приложение (на французском)", en="Английская версия",
   accueil_t="{nom}: бесплатные прогнозы по акциям и криптовалютам", accueil_h1="{nom}: прогнозы по бирже и крипте простыми словами",
   accueil_desc="Бесплатные прогнозы на месяц по французским, европейским и американским акциям, ETF и криптовалютам: ожидаемое движение и риск падения. Образовательный проект.",
   accueil_intro="Более 200 акций, ETF и криптовалют, автоматически анализируются каждый час. Бесплатно, без регистрации, в образовательных целях.",
   risque_t="Наибольший риск сильного падения в этом месяце", calmes_t="Самые спокойные в этом месяце", tous="Все акции и криптовалюты",
   avert="<b>На бирже нет ничего гарантированного.</b> {nom} — бесплатный образовательный проект. Эти данные создаются автоматически, могут содержать ошибки и не являются инвестиционным советом. Вы можете потерять все вложенные деньги.",
   marches={"fr": "Французские акции", "eu": "Европейские акции", "us": "Акции США", "crypto": "Криптовалюты", "etf": "ETF и индексы", "tendances": "В тренде"},
   langues="Языки"),
 "tr": dict(
   titre_page="{nom} ({tk}): bir aylık tahmin ve analiz", h1="{nom} ({tk}): bir aylık tahmin",
   desc="{nom} ({tk}): fiyat, beklenen hareket, sert düşüş riski ve yapay zekâ görüşü, her gün güncellenir. Ücretsiz eğitim projesi, yatırım tavsiyesi değildir.",
   maj="Otomatik güncellenir · {d} fiyatları", prix="son fiyat", perf="1 ayda",
   agit="bir ayda beklenen hareket", chute="%10'dan fazla düşüş riski", sens="{h} işlem günü sonra daha yüksek olma olasılığı",
   sans_avis="net bir görüş yok", sur10="10'da {n}",
   fiable_t="Ne güvenilir?", fiable=("Fiyatın bir ay sonra yükselip düşeceğini tahmin etmek neredeyse imkânsız: hiç görmedikleri yıllarda test edilen "
     "yapay zekâlarımız «hep yükselir» kuralından daha iyi değil. Buna karşılık fiyatın <b>ne kadar</b> hareket edeceğini ve <b>sert düşüş riskini</b> iyi tahmin ediyorlar."),
   app="Etkileşimli uygulamayı aç (Fransızca)", en="İngilizce sürüm",
   accueil_t="{nom}: hisse ve kripto için ücretsiz tahminler", accueil_h1="{nom}: borsa ve kripto tahminleri, basitçe anlatıldı",
   accueil_desc="Fransız, Avrupa ve ABD hisseleri, ETF'ler ve kripto paralar için ücretsiz bir aylık tahminler: beklenen hareket ve düşüş riski. Eğitim projesi.",
   accueil_intro="200'tan fazla hisse, ETF ve kripto para, her saat otomatik olarak analiz edilir. Ücretsiz, kayıt gerektirmez, eğitim amaçlı.",
   risque_t="Bu ay en yüksek sert düşüş riski", calmes_t="Bu ay en sakin beklenenler", tous="Tüm hisseler ve kripto paralar",
   avert="<b>Borsada hiçbir şey kesin değildir.</b> {nom} ücretsiz bir eğitim projesidir. Bu rakamlar otomatik üretilir, hata içerebilir ve yatırım tavsiyesi değildir. Yatırdığınız tüm parayı kaybedebilirsiniz.",
   marches={"fr": "Fransız hisseleri", "eu": "Avrupa hisseleri", "us": "ABD hisseleri", "crypto": "Kripto paralar", "etf": "ETF'ler ve endeksler", "tendances": "Trend olanlar"},
   langues="Diller"),
 "ar": dict(
   titre_page="{nom} ({tk}): توقع وتحليل لشهر واحد", h1="{nom} ({tk}): توقع لشهر واحد",
   desc="{nom} ({tk}): السعر، والحركة المتوقعة، وخطر الهبوط القوي، ورأي الذكاء الاصطناعي، يتم تحديثها يوميًا. مشروع تعليمي مجاني، وليس نصيحة استثمارية.",
   maj="يتم التحديث تلقائيًا · أسعار {d}", prix="آخر سعر", perf="خلال شهر",
   agit="الحركة المتوقعة خلال شهر", chute="خطر الهبوط بأكثر من 10 %", sens="احتمال أن يكون السعر أعلى بعد {h} جلسة تداول",
   sans_avis="لا رأي واضح", sur10="{n} من 10",
   fiable_t="ما الذي يمكن الوثوق به؟", fiable=("تخمين ما إذا كان السعر سيرتفع أو ينخفض خلال شهر شبه مستحيل: عند اختبارها على سنوات لم ترها من قبل، "
     "لم تتفوق نماذجنا على قاعدة «يرتفع دائمًا». لكنها تتوقع جيدًا <b>مقدار</b> تحرك السعر و<b>خطر الهبوط القوي</b>."),
   app="افتح التطبيق التفاعلي (بالفرنسية)", en="النسخة الإنجليزية",
   accueil_t="{nom}: توقعات مجانية للأسهم والعملات المشفرة", accueil_h1="{nom}: توقعات البورصة والعملات المشفرة بشرح بسيط",
   accueil_desc="توقعات مجانية لشهر واحد للأسهم الفرنسية والأوروبية والأمريكية وصناديق المؤشرات والعملات المشفرة: الحركة المتوقعة وخطر الهبوط. مشروع تعليمي.",
   accueil_intro="أكثر من 200 سهمًا وصندوقًا وعملة مشفرة، تُحلَّل تلقائيًا كل ساعة. مجاني، بدون تسجيل، لأغراض تعليمية.",
   risque_t="أعلى خطر هبوط قوي هذا الشهر", calmes_t="الأكثر هدوءًا المتوقع هذا الشهر", tous="كل الأسهم والعملات المشفرة",
   avert="<b>لا شيء مضمون في البورصة.</b> {nom} مشروع تعليمي مجاني. هذه الأرقام تُنشأ تلقائيًا، وقد تحتوي على أخطاء، وليست نصيحة استثمارية. قد تخسر كل المال الذي تستثمره.",
   marches={"fr": "أسهم فرنسية", "eu": "أسهم أوروبية", "us": "أسهم أمريكية", "crypto": "عملات مشفرة", "etf": "صناديق ومؤشرات", "tendances": "الأكثر تداولًا"},
   langues="اللغات"),
 "hi": dict(
   titre_page="{nom} ({tk}): एक महीने का पूर्वानुमान और विश्लेषण", h1="{nom} ({tk}): एक महीने का पूर्वानुमान",
   desc="{nom} ({tk}): भाव, अनुमानित उतार-चढ़ाव, तेज़ गिरावट का जोखिम और AI की राय, रोज़ अपडेट। मुफ़्त शैक्षिक परियोजना, निवेश सलाह नहीं।",
   maj="अपने आप अपडेट · {d} के भाव", prix="आख़िरी भाव", perf="1 महीने में",
   agit="एक महीने में अनुमानित उतार-चढ़ाव", chute="10 % से ज़्यादा गिरने का जोखिम", sens="{h} सत्रों बाद ऊपर होने की संभावना",
   sans_avis="कोई साफ़ राय नहीं", sur10="10 में से {n}",
   fiable_t="किस पर भरोसा करें?", fiable=("एक महीने बाद भाव ऊपर होगा या नीचे, यह बताना लगभग असंभव है: पहले कभी न देखे गए वर्षों पर परखने पर "
     "हमारे AI «हमेशा बढ़ता है» नियम से बेहतर नहीं निकले। लेकिन वे अच्छी तरह बताते हैं कि भाव <b>कितना</b> हिलेगा और <b>तेज़ गिरावट का जोखिम</b> कितना है।"),
   app="इंटरैक्टिव ऐप खोलें (फ़्रेंच में)", en="अंग्रेज़ी संस्करण",
   accueil_t="{nom}: शेयर और क्रिप्टो के मुफ़्त पूर्वानुमान", accueil_h1="{nom}: शेयर बाज़ार और क्रिप्टो पूर्वानुमान, आसान भाषा में",
   accueil_desc="फ़्रांसीसी, यूरोपीय और अमेरिकी शेयरों, ETF और क्रिप्टोकरेंसी के लिए एक महीने के मुफ़्त पूर्वानुमान: अनुमानित उतार-चढ़ाव और गिरावट का जोखिम। शैक्षिक परियोजना।",
   accueil_intro="200 से ज़्यादा शेयर, ETF और क्रिप्टोकरेंसी, हर घंटे अपने आप विश्लेषित। मुफ़्त, बिना रजिस्ट्रेशन, शैक्षिक।",
   risque_t="इस महीने तेज़ गिरावट का सबसे ज़्यादा जोखिम", calmes_t="इस महीने सबसे शांत रहने का अनुमान", tous="सभी शेयर और क्रिप्टोकरेंसी",
   avert="<b>शेयर बाज़ार में कुछ भी पक्का नहीं है।</b> {nom} एक मुफ़्त शैक्षिक परियोजना है। ये आँकड़े अपने आप बनते हैं, इनमें ग़लतियाँ हो सकती हैं और ये निवेश सलाह नहीं हैं। आप निवेश किया गया पूरा पैसा खो सकते हैं।",
   marches={"fr": "फ़्रांसीसी शेयर", "eu": "यूरोपीय शेयर", "us": "अमेरिकी शेयर", "crypto": "क्रिप्टोकरेंसी", "etf": "ETF और सूचकांक", "tendances": "ट्रेंड में"},
   langues="भाषाएँ"),
 "zh": dict(
   titre_page="{nom}（{tk}）：一个月预测与分析", h1="{nom}（{tk}）：一个月预测",
   desc="{nom}（{tk}）：价格、预计波动、大幅下跌风险和人工智能观点，每日更新。免费教育项目，不构成投资建议。",
   maj="自动更新 · {d} 的价格", prix="最新价格", perf="近 1 个月",
   agit="未来一个月预计波动", chute="下跌超过 10% 的风险", sens="{h} 个交易日后价格更高的概率",
   sans_avis="没有明确观点", sur10="10 次中 {n} 次",
   fiable_t="哪些预测可靠？", fiable=("预测一个月后价格涨还是跌几乎不可能：在从未见过的年份上测试时，我们的人工智能并不比“永远上涨”这条规则更好。"
     "但它们能较好地预测价格<b>波动幅度</b>以及<b>大幅下跌的风险</b>。"),
   app="打开互动应用（法语）", en="英文版",
   accueil_t="{nom}：免费的股票和加密货币预测", accueil_h1="{nom}：简单易懂的股市与加密货币预测",
   accueil_desc="法国、欧洲和美国股票、ETF 及加密货币的免费一个月预测：预计波动和下跌风险。教育项目。",
   accueil_intro="200 多只股票、ETF 和加密货币，每小时自动分析。免费、无需注册、仅供学习。",
   risque_t="本月大幅下跌风险最高", calmes_t="本月预计最平稳", tous="全部股票和加密货币",
   avert="<b>股市没有任何保证。</b>{nom} 是一个免费教育项目。这些数据自动生成，可能有误，不构成投资建议。您可能损失全部投入资金。",
   marches={"fr": "法国股票", "eu": "欧洲股票", "us": "美国股票", "crypto": "加密货币", "etf": "ETF 和指数", "tendances": "热门"},
   langues="语言"),
 "ja": dict(
   titre_page="{nom}（{tk}）：1か月予測と分析", h1="{nom}（{tk}）：1か月予測",
   desc="{nom}（{tk}）：価格、予想される変動、大幅下落リスク、AIの見方を毎日更新。無料の教育プロジェクトで、投資助言ではありません。",
   maj="自動更新 · {d} の価格", prix="直近の価格", perf="1か月",
   agit="今後1か月の予想変動", chute="10%超下落するリスク", sens="{h}営業日後に上がっている確率",
   sans_avis="明確な見方なし", sur10="10回中{n}回",
   fiable_t="何が信頼できる？", fiable=("1か月後に価格が上がるか下がるかを当てるのはほぼ不可能です。見たことのない年で検証すると、"
     "私たちのAIは「常に上がる」というルールより良くありませんでした。一方で、価格が<b>どれだけ</b>動くか、<b>大幅下落のリスク</b>はうまく予測できます。"),
   app="インタラクティブアプリを開く（フランス語）", en="英語版",
   accueil_t="{nom}：株式と暗号資産の無料予測", accueil_h1="{nom}：株式・暗号資産の予測をわかりやすく",
   accueil_desc="フランス・欧州・米国株、ETF、暗号資産の無料1か月予測：予想変動と下落リスク。教育プロジェクト。",
   accueil_intro="200以上の株式・ETF・暗号資産を毎時自動分析。無料、登録不要、学習用。",
   risque_t="今月、大幅下落リスクが最も高い銘柄", calmes_t="今月最も落ち着くと予想される銘柄", tous="すべての株式と暗号資産",
   avert="<b>相場に確実なものはありません。</b>{nom}は無料の教育プロジェクトです。数値は自動で作成され、誤りを含む可能性があり、投資助言ではありません。投資したお金をすべて失う可能性があります。",
   marches={"fr": "フランス株", "eu": "欧州株", "us": "米国株", "crypto": "暗号資産", "etf": "ETF・指数", "tendances": "話題の銘柄"},
   langues="言語"),
 "ko": dict(
   titre_page="{nom} ({tk}): 한 달 전망과 분석", h1="{nom} ({tk}): 한 달 전망",
   desc="{nom} ({tk}): 가격, 예상 변동 폭, 급락 위험, AI 의견을 매일 업데이트합니다. 무료 교육 프로젝트이며 투자 조언이 아닙니다.",
   maj="자동 업데이트 · {d} 가격", prix="최근 가격", perf="1개월",
   agit="향후 한 달 예상 변동 폭", chute="10% 넘게 하락할 위험", sens="{h}거래일 뒤 더 높을 확률",
   sans_avis="뚜렷한 의견 없음", sur10="10번 중 {n}번",
   fiable_t="무엇을 믿을 수 있나요?", fiable=("한 달 뒤 가격이 오를지 내릴지 맞히는 것은 거의 불가능합니다. 본 적 없는 해로 검증했을 때 "
     "우리 AI는 '항상 오른다' 규칙보다 낫지 않았습니다. 대신 가격이 <b>얼마나</b> 움직일지와 <b>급락 위험</b>은 잘 예측합니다."),
   app="인터랙티브 앱 열기 (프랑스어)", en="영어 버전",
   accueil_t="{nom}: 주식과 암호화폐 무료 전망", accueil_h1="{nom}: 주식·암호화폐 전망을 쉽게",
   accueil_desc="프랑스·유럽·미국 주식, ETF, 암호화폐의 무료 한 달 전망: 예상 변동 폭과 하락 위험. 교육 프로젝트.",
   accueil_intro="200개가 넘는 주식, ETF, 암호화폐를 매시간 자동 분석합니다. 무료, 가입 불필요, 교육용.",
   risque_t="이번 달 급락 위험이 가장 높은 종목", calmes_t="이번 달 가장 잠잠할 것으로 예상되는 종목", tous="모든 주식과 암호화폐",
   avert="<b>주식 시장에 확실한 것은 없습니다.</b> {nom}은(는) 무료 교육 프로젝트입니다. 이 수치는 자동으로 만들어지며 오류가 있을 수 있고 투자 조언이 아닙니다. 투자한 돈을 모두 잃을 수 있습니다.",
   marches={"fr": "프랑스 주식", "eu": "유럽 주식", "us": "미국 주식", "crypto": "암호화폐", "etf": "ETF·지수", "tendances": "화제 종목"},
   langues="언어"),
}


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _nombre(v, dec, sep):
    txt = f"{v:,.{dec}f}"
    if sep == ",":
        txt = txt.replace(",", " ").replace(".", ",")
    return txt


def _px(v, dev, sep):
    if v is None:
        return "–"
    if abs(v) >= 1 or v == 0:
        txt = _nombre(v, 2, sep)
    else:
        txt = f"{v:.{max(2, 3 - math.floor(math.log10(abs(v))))}f}"
        if sep == ",":
            txt = txt.replace(".", ",")
    return f"{txt} {'€' if dev == '€' else '$'}"


def _pc(v, sep, signe=True):
    if v is None:
        return "–"
    txt = f"{v * 100:.1f}"
    if sep == ",":
        txt = txt.replace(".", ",")
    cls = "up" if v > 0 else "down" if v < 0 else ""
    return f'<span class="m {cls}">{"+" if signe and v > 0 else ""}{txt} %</span>'


def chemin_titre(lg: str, s: str) -> str:
    return {"fr": f"titres/{s}.html", "en": f"en/stocks/{s}.html"}.get(lg, f"{lg}/stocks/{s}.html")


def chemin_accueil(lg: str) -> str:
    return {"fr": "", "en": "en/index.html"}.get(lg, f"{lg}/index.html")


def alternates_titre(s: str) -> dict:
    d = {lg: chemin_titre(lg, s) for lg in TOUTES}
    d["x-default"] = d["fr"]
    return d


def alternates_accueil() -> dict:
    d = {lg: chemin_accueil(lg) for lg in TOUTES}
    d["x-default"] = ""
    return d


def selecteur(prefixe: str, actuel: str, chemins: dict) -> str:
    """Liste des langues (lien vers la même page dans chaque langue)."""
    return " · ".join(f"<b>{_e(NOMS_LANGUES[lg])}</b>" if lg == actuel else
                      f"<a href='{prefixe}{chemins[lg] or 'index.html'}' hreflang='{lg}' lang='{lg}'>{_e(NOMS_LANGUES[lg])}</a>"
                      for lg in TOUTES)


def _page(lg, base, titre, desc, chemin, corps, csp, alternates):
    nom_lg, locale, sens, _ = LANGUES[lg]
    L = T[lg]
    prefixe = "../" * chemin.count("/")
    titre, desc = seo.titre_court(titre), seo.desc_courte(desc)
    etapes = [(f"{NOM} ({nom_lg})", f"{lg}/index.html")] + ([(titre, chemin)] if chemin != f"{lg}/index.html" else [])
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": titre, "description": desc, "inLanguage": lg,
         "isPartOf": {"@type": "WebSite", "name": NOM, "url": base or None}},
        seo._jsonld_fil(base, etapes)]}
    tete = seo.balises_tete(base, titre, desc, chemin, jsonld=jsonld, alternates=alternates, langue=lg)
    csp = seo.csp_avec_stats(csp)
    return f"""<!doctype html>
<html lang="{lg}" dir="{sens}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{f'<meta http-equiv="Content-Security-Policy" content="{csp}">' if csp else ''}
<title>{_e(titre)}</title>
{tete}
<link rel="icon" href="{prefixe}icone-192.png">
{seo.SCRIPT_THEME}
{seo.POLICES}
{seo.script_stats()}
<style>{seo.CSS_PAGE}</style>
</head>
<body>
{seo.entete(prefixe, chemin, f"{lg}/index.html", nom_lg,
            [(L['tous'], f"{lg}/index.html"), ("English", "en/index.html", 'hreflang="en" lang="en"'), ("Français", "index.html", 'hreflang="fr" lang="fr"')],
            None, aria_nav=NOM, aria_theme="☀ / ☾", aller=NOM)}
<div class="w">
<main id="contenu" tabindex="-1">
{corps}
</main>
<footer><p class="avert">{L['avert'].format(nom=NOM)}</p>
<p class="muted">{_e(L['langues'])}: {selecteur(prefixe, lg, alternates)}</p></footer>
</div>
{seo.SCRIPT_BOUTON}
</body></html>
"""


def _page_titre(lg, base, t, horizon, date, csp=""):
    L = T[lg]
    sep = LANGUES[lg][3]
    dev, p = t.get("devise", "$"), t.get("proba_hausse")
    nom, tk = t["nom"], seo.aff_tk(t["ticker"])
    s = seo.slug(t["ticker"])
    chemin = chemin_titre(lg, s)
    rp = t.get("risque_prevu") or {}
    mv, ch = rp.get("mouvement"), rp.get("chute")
    net = p is not None and t.get("avis_net") is not False
    cases = [(_px(t.get("prix"), dev, sep), L["prix"]), (_pc((t.get("perf") or {}).get("1 mois"), sep), L["perf"])]
    if mv:
        cases.append((f"±{_pc(mv, sep, signe=False)}", L["agit"]))
    if rp.get("semaine"):
        cases.append((f"±{_pc(rp['semaine'], sep, signe=False)}", AGIT_SEMAINE[lg]))
    if ch is not None:
        cases.append((f"{round(ch * 100)} %", L["chute"]))
    cases.append((L["sur10"].format(n=round(p * 10)) if net else L["sans_avis"], L["sens"].format(h=horizon)))
    corps = (f"<h1>{_e(L['h1'].format(nom=nom, tk=tk))}</h1><p class='muted'>{_e(L['maj'].format(d=date))}</p>"
             "<div class='carte grille'>" + "".join(f"<div class='k'><b><bdi>{v}</bdi></b><span>{_e(lib)}</span></div>" for v, lib in cases) + "</div>"
             f"<h2>{_e(L['fiable_t'])}</h2><p>{L['fiable']}</p>"
             f"<p><a class='btn' href='../../index.html#{_e(re.sub(r'[^A-Za-z0-9._-]', '', t['ticker']))}'>{_e(L['app'])}</a> "
             f"<a class='btn ghost' href='../../en/stocks/{s}.html' hreflang='en'>{_e(L['en'])}</a></p>")
    return chemin, _page(lg, base, L["titre_page"].format(nom=nom, tk=tk) + f" | {NOM}", L["desc"].format(nom=nom, tk=tk),
                         chemin, corps, csp, alternates_titre(s))


def generer(payload: dict, dossier: str, csp: str, base: str) -> list:
    """Écrit <langue>/index.html et <langue>/stocks/*.html pour chaque langue. Renvoie les entrées du sitemap."""
    date = payload.get("date_donnees", "")
    horizon = payload.get("horizon", 20)
    titres = [t for t in payload.get("titres", []) if t.get("prix")]
    urls = []
    for lg in LANGUES:
        L = T[lg]
        sep = LANGUES[lg][3]
        os.makedirs(os.path.join(dossier, lg, "stocks"), exist_ok=True)
        for t in titres:
            chemin, page = _page_titre(lg, base, t, horizon, date, csp)
            with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
                f.write(page)
            urls.append((chemin, "daily", "0.4"))
        lien = lambda t: f"<a href='stocks/{seo.slug(t['ticker'])}.html'>{_e(t['nom'])}</a>"
        rq = sorted([t for t in titres if (t.get("risque_prevu") or {}).get("chute") is not None],
                    key=lambda t: -t["risque_prevu"]["chute"])[:10]
        calmes = sorted([t for t in titres if t.get("marche") in ("fr", "eu", "us") and (t.get("risque_prevu") or {}).get("mouvement")],
                        key=lambda t: t["risque_prevu"]["mouvement"])[:10]
        tab = lambda lst, f: "<div class='carte'><table>" + "".join(f"<tr><td>{lien(t)} <span class='muted'>({_e(seo.aff_tk(t['ticker']))})</span></td><td class='m'><bdi>{f(t)}</bdi></td></tr>" for t in lst) + "</table></div>"
        groupes = ""
        for cle, lib in L["marches"].items():
            items = [t for t in titres if t.get("marche") == cle]
            if items:
                groupes += f"<h3>{_e(lib)}</h3><ul class='liste'>" + "".join(f"<li>{lien(t)}</li>" for t in items) + "</ul>"
        corps = (f"<h1>{_e(L['accueil_h1'].format(nom=NOM))}</h1><p class='muted'>{_e(L['accueil_intro'])}</p>"
                 f"<p><a class='btn' href='../index.html'>{_e(L['app'])}</a> <a class='btn ghost' href='../en/index.html' hreflang='en'>{_e(L['en'])}</a></p>"
                 f"<h2>{_e(L['fiable_t'])}</h2><p>{L['fiable']}</p>"
                 + (f"<h2>{_e(L['risque_t'])}</h2>" + tab(rq, lambda t: f"{round(t['risque_prevu']['chute'] * 100)} %") if rq else "")
                 + (f"<h2>{_e(L['calmes_t'])}</h2>" + tab(calmes, lambda t: f"±{_pc(t['risque_prevu']['mouvement'], sep, signe=False)}") if calmes else "")
                 + f"<h2 id='all'>{_e(L['tous'])}</h2>{groupes}")
        chemin = f"{lg}/index.html"
        with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
            f.write(_page(lg, base, L["accueil_t"].format(nom=NOM), L["accueil_desc"], chemin, corps, csp, alternates_accueil()))
        urls.append((chemin, "daily", "0.7"))
    return urls
