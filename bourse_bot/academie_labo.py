"""Version 77 : les « labos » de l'Académie — de petits simulateurs à manipuler au milieu d'une leçon.

Chaque labo est un bloc <div class="labo" data-labo="nom"> rempli par JS_LABO. Sans JavaScript, un texte de remplacement s'affiche.
Les formules sont volontairement simples et écrites en clair : elles sont rejouées en Python par verif_academie.py.
Taux d'imposition utilisés par le labo « fiscal » : ceux de 2026 (PFU 31,4 %, prélèvements sociaux 18,6 %).
"""

PFU = 31.4          # prélèvement forfaitaire unique 2026, en %
PS = 18.6           # prélèvements sociaux 2026 (PEA de plus de 5 ans), en %

NOMS = {
    "offre": "Fais bouger le prix",
    "pertes": "Combien faut-il regagner ?",
    "composes": "Ta boule de neige",
    "frais": "Ce que les frais te coûtent",
    "dca": "Investir chaque mois ou tout d'un coup",
    "per": "Calcule un PER et un rendement",
    "diversif": "Combien d'actions pour être diversifié ?",
    "fiscal": "Compte-titres ou PEA : ce qu'il te reste",
    "obligation": "Le prix d'une obligation quand les taux bougent",
    "change": "Action et devise : l'effet combiné",
    "levier": "Le levier, dans les deux sens",
}


def bloc(nom, reglages=None):
    """Le bloc HTML d'un labo, placé sous une mini-leçon. reglages : valeurs de départ, par exemple {"l": 100}."""
    attrs = "".join(f" data-{k}='{v}'" for k, v in (reglages or {}).items())
    return (f"<div class='labo' data-labo='{nom}'{attrs}><p class='labo-t'><span>À toi de jouer</span>{NOMS[nom]}</p>"
            "<div class='labo-c'><noscript>Ce simulateur a besoin de JavaScript pour fonctionner.</noscript></div></div>")


CSS_LABO = """
.labo{margin:20px 0 6px;border:1px solid var(--a-line);border-radius:14px;background:var(--a-card);overflow:hidden}
.labo-t{margin:0;padding:12px 18px;font-weight:600;font-size:16.5px;border-bottom:1px solid var(--a-line);background:var(--a-card2)}
.labo-t span{display:block;font-size:12px;font-weight:600;color:var(--a-prim);letter-spacing:.02em;margin-bottom:1px}
.labo-c{padding:16px 18px 18px;font-size:15.5px;line-height:1.55}
.labo-ch{display:grid;grid-template-columns:1fr auto;gap:2px 12px;align-items:center;margin:0 0 12px}
.labo-ch label{font-size:14.5px;color:var(--a-muted)}.labo-ch output{font-family:var(--m);font-weight:600;font-variant-numeric:tabular-nums}
.labo-ch input[type=range]{grid-column:1/-1;width:100%;accent-color:var(--a-prim);height:28px;margin:0}
.labo-ch select{grid-column:1/-1;font:inherit;padding:8px 10px;border-radius:8px;border:1px solid var(--a-line);background:var(--a-card);color:var(--a-ink)}
.labo-res{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:14px 0 10px}
.labo-res div{padding:10px 12px;border-radius:10px;background:var(--a-card2)}
.labo-res b{display:block;font-family:var(--m);font-size:19px;font-variant-numeric:tabular-nums;line-height:1.25}
.labo-res span{font-size:12.5px;color:var(--a-muted)}
.labo-res .ok b{color:var(--a-ok)}.labo-res .ko b{color:var(--a-ko)}.labo-res .pr b{color:var(--a-prim)}
.labo-ph{margin:10px 0 0;padding:10px 12px;border-left:3px solid var(--a-prim);background:var(--a-soft);border-radius:0 8px 8px 0;font-size:15px}
.labo-note{margin:10px 0 0;font-size:13px;color:var(--a-muted)}
.labo svg{width:100%;height:auto;display:block;margin-top:6px;overflow:visible}
.labo .lg-a{fill:none;stroke:var(--a-prim);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.labo .lg-b{fill:none;stroke:var(--a-or);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:6 5}
.labo .lg-za{fill:color-mix(in srgb,var(--a-prim) 16%,transparent)}.labo .lg-zb{fill:color-mix(in srgb,var(--a-muted) 18%,transparent)}
.labo .lg-ax{stroke:var(--a-line);stroke-width:1.2}.labo .lg-tx{fill:var(--a-muted);font-size:11px;font-family:var(--f)}
.labo .lg-pt{fill:var(--a-prim)}.labo .lg-bar-a{fill:var(--a-prim)}.labo .lg-bar-b{fill:var(--a-or)}.labo .lg-bar-ko{fill:var(--a-ko)}.labo .lg-bar-ok{fill:var(--a-ok)}.labo .lg-bar-g{fill:var(--a-gris,var(--a-line))}
.labo-leg{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--a-muted);margin-top:6px}
.labo-leg i{display:inline-block;width:14px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px;background:var(--a-prim)}
.labo-leg i.b{background:var(--a-or)}.labo-leg i.g{background:var(--a-muted)}
@media (prefers-reduced-motion:no-preference){.labo-res b{transition:color .2s}}
"""

JS_LABO = r"""<script>
(function(){
  const eur=(x,d)=>x.toLocaleString("fr-FR",{maximumFractionDigits:d||0,minimumFractionDigits:d||0})+" €";
  const nb=(x,d)=>x.toLocaleString("fr-FR",{maximumFractionDigits:d==null?1:d,minimumFractionDigits:0});
  const pc=(x,d)=>{const r=+(+x).toFixed(d==null?1:d); return (r>0?"+":r<0?"−":"")+nb(Math.abs(r),d)+" %";};
  const W=560,H=190,G=42,D=10,T=12,B=26;
  function courbes(series,opt){ // series : [{v:[...],c:"lg-a",zone:"lg-za"}], axe x = index
    opt=opt||{}; const all=series.flatMap(s=>s.v); let mn=opt.min!=null?opt.min:Math.min(...all), mx=Math.max(...all); if(mx===mn)mx=mn+1;
    const n=series[0].v.length, X=i=>G+(W-G-D)*i/Math.max(1,n-1), Y=v=>T+(H-T-B)*(1-(v-mn)/(mx-mn));
    let s="<svg viewBox='0 0 "+W+" "+H+"' role='img' aria-label='"+(opt.alt||"Graphique")+"'>";
    for(let k=0;k<=2;k++){const v=mn+(mx-mn)*k/2,y=Y(v); s+="<line class='lg-ax' x1='"+G+"' x2='"+(W-D)+"' y1='"+y+"' y2='"+y+"'/><text class='lg-tx' x='"+(G-6)+"' y='"+(y+4)+"' text-anchor='end'>"+(opt.fmt?opt.fmt(v):nb(v,0))+"</text>";}
    series.forEach(se=>{const p=se.v.map((v,i)=>(i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1)).join(" ");
      if(se.zone) s+="<path class='"+se.zone+"' d='"+p+" L"+X(n-1).toFixed(1)+" "+Y(mn)+" L"+X(0)+" "+Y(mn)+" Z'/>";
      s+="<path class='"+se.c+"' d='"+p+"'/>";});
    if(opt.pt!=null){const se=series[0]; s+="<circle class='lg-pt' r='5' cx='"+X(opt.pt).toFixed(1)+"' cy='"+Y(se.v[opt.pt]).toFixed(1)+"'/>";}
    (opt.xl||[]).forEach(([i,t])=>{s+="<text class='lg-tx' x='"+X(i).toFixed(1)+"' y='"+(H-8)+"' text-anchor='"+(i===0?"start":i>=n-1?"end":"middle")+"'>"+t+"</text>";});
    return s+"</svg>";
  }
  function barres(items,opt){ // items : [{l,v,c,t}]
    opt=opt||{}; const mx=Math.max(...items.map(i=>Math.abs(i.v)),opt.max||0)||1, h=30, gap=12, HH=items.length*(h+gap)+4, L=150;
    let s="<svg viewBox='0 0 "+W+" "+HH+"' role='img' aria-label='"+(opt.alt||"Comparaison")+"'>";
    items.forEach((it,k)=>{const y=k*(h+gap)+2, w=Math.max(2,(W-L-90)*Math.abs(it.v)/mx);
      s+="<text class='lg-tx' x='0' y='"+(y+h/2+4)+"' style='font-size:12.5px'>"+it.l+"</text><rect class='"+(it.c||"lg-bar-a")+"' x='"+L+"' y='"+y+"' width='"+w.toFixed(1)+"' height='"+h+"' rx='5'/>"
        +"<text class='lg-tx' x='"+(L+w+8).toFixed(1)+"' y='"+(y+h/2+4)+"' style='font-size:13px;font-weight:600;fill:var(--a-ink)'>"+it.t+"</text>";});
    return s+"</svg>";
  }
  const res=l=>"<div class='labo-res'>"+l.map(([t,v,c])=>"<div class='"+(c||"")+"'><b>"+v+"</b><span>"+t+"</span></div>").join("")+"</div>";
  const leg=l=>"<div class='labo-leg'>"+l.map(([c,t])=>"<span><i class='"+c+"'></i>"+t+"</span>").join("")+"</div>";
  const L={
    offre:{ch:[["a","Personnes qui veulent acheter",0,100,5,60,v=>v],["v","Personnes qui veulent vendre",0,100,5,40,v=>v]],
      f(o){const t=o.a+o.v, ec=t?(o.a-o.v)/t:0, p=20*(1+0.25*ec);
        return res([["prix de départ","20,00 €"],["prix après les échanges",eur(p,2),p>20.004?"ok":p<19.996?"ko":""],["variation",pc((p/20-1)*100,1),ec>0?"ok":ec<0?"ko":""]])
          +barres([{l:"Acheteurs",v:o.a,c:"lg-bar-ok",t:o.a},{l:"Vendeurs",v:o.v,c:"lg-bar-ko",t:o.v}],{max:100,alt:"Acheteurs et vendeurs"})
          +"<p class='labo-ph'>"+(ec>0.02?"Plus d'acheteurs que de vendeurs : pour être servis, certains acceptent de payer plus cher. Le prix monte.":ec<-0.02?"Plus de vendeurs que d'acheteurs : pour trouver preneur, certains acceptent de vendre moins cher. Le prix baisse.":"Autant d'acheteurs que de vendeurs : le prix ne bouge presque pas.")+"</p>"
          +"<p class='labo-note'>Modèle très simplifié, pour sentir le mécanisme : dans la réalité, chaque acheteur et chaque vendeur a son propre prix.</p>";}},
    pertes:{ch:[["p","Perte subie",5,90,5,50,v=>"−"+v+" %"]],
      f(o){const r=1000*(1-o.p/100), g=o.p/(100-o.p)*100;
        return res([["il te reste, sur 1 000 €",eur(r),"ko"],["hausse nécessaire pour revenir",pc(g,1),"pr"]])
          +barres([{l:"Au départ",v:1000,c:"lg-bar-g",t:"1 000 €"},{l:"Après la perte",v:r,c:"lg-bar-ko",t:eur(r)},{l:"Chemin à refaire",v:1000-r,c:"lg-bar-a",t:pc(g,1)}],{max:1000})
          +"<p class='labo-ph'>Après une perte de "+o.p+" %, il faut gagner "+nb(g,1)+" % pour retrouver sa mise"+(o.p>=50?" : au moins le double de ce qui a été perdu.":". Plus la perte est grande, plus l'écart se creuse.")+"</p>";}},
    composes:{ch:[["c","Somme de départ",0,20000,500,1000,v=>eur(v)],["m","Versement chaque mois",0,500,10,50,v=>eur(v)],["t","Rendement par an",0,10,0.5,5,v=>nb(v,1)+" %"],["n","Durée",1,40,1,20,v=>v+" ans"]],
      f(o){const tm=Math.pow(1+o.t/100,1/12)-1, tot=[o.c], ver=[o.c]; let x=o.c;
        for(let k=1;k<=o.n*12;k++){x=x*(1+tm)+o.m; if(k%12===0){tot.push(x); ver.push(o.c+o.m*k);}}
        const v=ver[ver.length-1], g=x-v;
        return res([["à la fin",eur(x),"pr"],["dont versé par toi",eur(v)],["dont gains",eur(g),"ok"]])
          +courbes([{v:tot,c:"lg-a",zone:"lg-za"},{v:ver,c:"lg-b"}],{min:0,fmt:v=>nb(v/1000,0)+" k€",xl:[[0,"aujourd'hui"],[o.n,"dans "+o.n+" ans"]],alt:"Évolution du capital"})
          +leg([["","Ton capital"],["b","Ce que tu as versé"]])
          +"<p class='labo-ph'>"+(v>0&&g>v?"Les gains ("+eur(g)+") dépassent ce que tu as versé : c'est le temps qui a fait le plus gros du travail.":"Allonge la durée : regarde comme l'écart entre les deux courbes s'ouvre de plus en plus vite.")+"</p>"
          +"<p class='labo-note'>Rendement régulier supposé, sans frais ni impôts. En Bourse, aucune année ne ressemble à la moyenne.</p>";}},
    frais:{ch:[["c","Somme placée",1000,50000,1000,10000,v=>eur(v)],["r","Rendement avant frais",2,10,0.5,6,v=>nb(v,1)+" % par an"],["a","Frais du placement A",0,1,0.05,0.2,v=>nb(v,2)+" % par an"],["b","Frais du placement B",0.5,3,0.1,1.2,v=>nb(v,1)+" % par an"],["n","Durée",5,40,1,30,v=>v+" ans"]],
      f(o){const A=[],Bv=[]; for(let k=0;k<=o.n;k++){A.push(o.c*Math.pow(1+(o.r-o.a)/100,k)); Bv.push(o.c*Math.pow(1+(o.r-o.b)/100,k));}
        const a=A[o.n], b=Bv[o.n];
        return res([["placement A",eur(a),"pr"],["placement B",eur(b)],["écart",eur(a-b),"ko"]])
          +courbes([{v:A,c:"lg-a"},{v:Bv,c:"lg-b"}],{min:0,fmt:v=>nb(v/1000,0)+" k€",xl:[[0,"aujourd'hui"],[o.n,"dans "+o.n+" ans"]],alt:"Deux placements identiques, frais différents"})
          +leg([["","A : "+nb(o.a,2)+" % de frais"],["b","B : "+nb(o.b,1)+" % de frais"]])
          +"<p class='labo-ph'>Même placement, même durée. La seule différence, ce sont les frais : "+eur(a-b)+" de moins à l'arrivée, soit "+nb((a-b)/a*100,0)+" % du résultat.</p>";}},
    dca:{ch:[["s","Ce que fait le marché pendant 12 mois",0,0,0,0,null,["Une chute, puis un rebond","Une hausse régulière","Des montagnes russes","Une baisse qui dure"]]],
      P:[[10,9,8,7,6.5,7,7.5,8,8.5,9,9.5,10],[10,10.3,10.6,10.9,11.2,11.5,11.8,12.1,12.4,12.7,13,13.3],[10,12,9,11,8,10,13,9,11,12,10,11],[10,9.6,9.2,8.9,8.6,8.4,8.2,8,7.8,7.6,7.5,7.4]],
      f(o){const p=this.P[o.s], fin=p[11]; let parts=0; const vd=[],vu=[]; const pu=1200/p[0];
        p.forEach((x,i)=>{parts+=100/x; vd.push(parts*x+100*(11-i)); vu.push(pu*x);});
        const d=parts*fin, u=pu*fin, moy=1200/parts;
        return res([["100 € chaque mois",eur(d),d>=u?"ok":""],["1 200 € d'un coup",eur(u),u>d?"ok":""],["prix moyen payé chaque mois",eur(moy,2),"pr"]])
          +courbes([{v:vd,c:"lg-a"},{v:vu,c:"lg-b"}],{fmt:v=>nb(v,0)+" €",xl:[[0,"mois 1"],[11,"mois 12"]],alt:"Valeur des deux stratégies"})
          +leg([["","100 € chaque mois (argent pas encore investi compris)"],["b","1 200 € dès le premier mois"]])
          +"<p class='labo-ph'>"+(d>u+1?"Ici, investir chaque mois fait mieux : tu as acheté plus de parts quand elles étaient bon marché.":u>d+1?"Ici, tout investir d'un coup fait mieux : le marché a monté presque sans pause, et l'argent en attente n'en a pas profité.":"Ici, les deux méthodes finissent presque au même point.")
          +" Le parcours est aussi plus calme : la courbe mensuelle descend moins bas.</p>"
          +"<p class='labo-note'>Prix inventés pour l'exemple. Personne ne sait à l'avance lequel de ces quatre scénarios va se produire.</p>";}},
    per:{ch:[["c","Cours de l'action",5,300,5,45,v=>eur(v)],["b","Bénéfice par action",0.5,20,0.5,3,v=>eur(v,2)],["d","Dividende par action",0,10,0.1,1.2,v=>eur(v,2)]],
      f(o){const per=o.c/o.b, rd=o.d/o.c*100, dist=o.d/o.b*100;
        return res([["PER",nb(per,1),"pr"],["rendement du dividende",nb(rd,1)+" %"],["part du bénéfice distribuée",nb(dist,0)+" %",dist>100?"ko":""]])
          +"<p class='labo-ph'>Tu paies "+nb(per,1)+" fois le bénéfice annuel. "+(per<10?"C'est bas : soit l'action est bon marché, soit le marché doute de l'avenir de l'entreprise.":per<=22?"C'est une zone courante pour une entreprise établie.":"C'est élevé : le marché attend une forte croissance, et la déception coûterait cher.")
          +(dist>100?" Attention : l'entreprise distribue plus qu'elle ne gagne, ce dividende est fragile.":"")+"</p>"
          +"<p class='labo-note'>Un ratio ne se juge que comparé : au secteur, et au passé de l'entreprise.</p>";}},
    diversif:{ch:[["n","Nombre d'actions dans le portefeuille",1,50,1,1,v=>v]],
      f(o){const vol=n=>30*Math.sqrt(1/n+(1-1/n)*0.25), c=[]; for(let k=1;k<=50;k++)c.push(vol(k));
        return res([["poids d'une faillite",nb(100/o.n,1)+" %","ko"],["agitation du portefeuille",nb(vol(o.n),1)+" % par an","pr"],["agitation d'une action seule","30 %"]])
          +courbes([{v:c,c:"lg-a",zone:"lg-za"}],{min:0,pt:o.n-1,fmt:v=>nb(v,0)+" %",xl:[[0,"1 action"],[24,"25"],[49,"50 actions"]],alt:"Agitation selon le nombre d'actions"})
          +"<p class='labo-ph'>"+(o.n<5?"Avec si peu de lignes, une seule mauvaise nouvelle pèse très lourd.":o.n<20?"Le risque baisse vite au début : chaque action ajoutée compte.":"Au-delà d'une vingtaine d'actions, la courbe s'aplatit : il reste le risque du marché entier, qu'aucune action de plus ne retire.")+"</p>"
          +"<p class='labo-note'>Ordre de grandeur : actions de même agitation (30 % par an), moyennement liées entre elles.</p>";}},
    fiscal:{ch:[["g","Ton gain à la vente",100,10000,100,1000,v=>eur(v)]],
      f(o){const cto=o.g*__PFU__/100, pea=o.g*__PS__/100;
        return res([["compte-titres : il te reste",eur(o.g-cto,2)],["PEA de plus de 5 ans : il te reste",eur(o.g-pea,2),"ok"],["différence",eur(cto-pea,2),"pr"]])
          +barres([{l:"Impôt en compte-titres",v:cto,c:"lg-bar-ko",t:eur(cto,2)+" (__PFUT__ %)"},{l:"Impôt en PEA (+5 ans)",v:pea,c:"lg-bar-b",t:eur(pea,2)+" (__PST__ %)"}],{max:o.g*0.4})
          +"<p class='labo-ph'>Sur le même gain, le PEA de plus de 5 ans te laisse "+eur(cto-pea,2)+" de plus. Et tant que rien ne sort du PEA, il n'y a aucun impôt à payer.</p>"
          +"<p class='labo-note'>Taux 2026. Cas simple : gain réalisé depuis 2026, sans option pour le barème. Avant 5 ans, un retrait de PEA est taxé comme un compte-titres.</p>";}},
    obligation:{ch:[["r","Taux du marché aujourd'hui",0.5,8,0.25,3,v=>nb(v,2)+" %"],["n","Années restantes avant le remboursement",1,20,1,10,v=>v+" ans"]],
      f(o){const px=(r,n)=>{let s=0;for(let k=1;k<=n;k++)s+=30/Math.pow(1+r/100,k);return s+1000/Math.pow(1+r/100,n);}; const p=px(o.r,o.n), c=[]; for(let r=0.5;r<=8.001;r+=0.25)c.push(px(r,o.n));
        return res([["prix de l'obligation",eur(p),p<999.5?"ko":p>1000.5?"ok":""],["par rapport à 1 000 €",pc((p/1000-1)*100,1),p<999.5?"ko":p>1000.5?"ok":""],["coupon versé chaque année","30 €"]])
          +courbes([{v:c,c:"lg-a",zone:"lg-za"}],{pt:Math.round((o.r-0.5)/0.25),fmt:v=>nb(v,0)+" €",xl:[[0,"taux 0,5 %"],[10,"3 %"],[30,"8 %"]],alt:"Prix selon le taux du marché"})
          +"<p class='labo-ph'>Cette obligation de 1 000 € verse 3 % par an. "+(o.r>3.01?"Les nouvelles obligations rapportent "+nb(o.r,2)+" % : pour vendre la tienne, il faut baisser son prix.":o.r<2.99?"Les nouvelles obligations ne rapportent que "+nb(o.r,2)+" % : la tienne est recherchée, son prix monte.":"Le marché offre le même taux : elle vaut son prix de départ.")
          +" Change la durée : plus l'échéance est loin, plus le prix réagit.</p>";}},
    change:{ch:[["a","L'action (en dollars)",-30,30,1,10,v=>pc(v,0)],["d","Le dollar face à l'euro",-20,20,1,-10,v=>pc(v,0)]],
      f(o){const r=((1+o.a/100)*(1+o.d/100)-1)*100;
        return res([["ton résultat en euros",pc(r,1),r>0?"ok":r<0?"ko":""],["la simple addition donnerait",pc(o.a+o.d,0)]])
          +barres([{l:"Action",v:o.a,c:o.a>=0?"lg-bar-ok":"lg-bar-ko",t:pc(o.a,0)},{l:"Dollar",v:o.d,c:o.d>=0?"lg-bar-ok":"lg-bar-ko",t:pc(o.d,0)},{l:"Résultat en euros",v:r,c:"lg-bar-a",t:pc(r,1)}],{max:30})
          +"<p class='labo-ph'>Le calcul : (1 "+(o.a>=0?"+":"−")+" "+nb(Math.abs(o.a)/100,2)+") × (1 "+(o.d>=0?"+":"−")+" "+nb(Math.abs(o.d)/100,2)+") − 1 = "+pc(r,1)+". Les deux effets se multiplient ; pour de petites variations, l'addition donne presque le même chiffre.</p>";}},
    levier:{ch:[["l","Effet de levier",1,100,1,5,v=>"×"+v],["v","Variation du marché",-30,30,0.5,-4,v=>pc(v,1)]],
      f(o){const brut=o.l*o.v, r=Math.max(-100,brut), fin=1000*(1+r/100), seuil=100/o.l;
        return res([["résultat sur ta mise",pc(r,0),r>0?"ok":"ko"],["il te reste, sur 1 000 €",eur(fin),r>0?"ok":"ko"],["tout est perdu dès que le marché fait","−"+nb(seuil,1)+" %","pr"]])
          +barres([{l:"Sans levier",v:o.v,c:o.v>=0?"lg-bar-ok":"lg-bar-ko",t:pc(o.v,1)},{l:"Avec levier ×"+o.l,v:r,c:r>=0?"lg-bar-ok":"lg-bar-ko",t:pc(r,0)}],{max:100})
          +"<p class='labo-ph'>"+(r<=-100?"La position est liquidée : la mise est entièrement perdue, même si le marché remonte ensuite.":"Avec un levier de "+o.l+", une baisse de "+nb(seuil,1)+" % suffit à tout perdre. "+(o.l>=20?"Une telle variation arrive en une séance ordinaire.":"Sur une action, cela arrive plusieurs fois par an."))+"</p>";}}
  };
  document.querySelectorAll(".labo[data-labo]").forEach(el=>{
    const def=L[el.dataset.labo]; if(!def) return; const c=el.querySelector(".labo-c"); const o={}; const id="lb"+Math.random().toString(36).slice(2,7);
    const out=document.createElement("div"); out.setAttribute("aria-live","polite"); c.innerHTML="";
    def.ch.forEach(([k,lab,mn,mx,pas,val,fmt,opts])=>{ const d=document.createElement("div"); d.className="labo-ch"; const val0=(el.dataset[k]!=null&&!opts)?+el.dataset[k]:val; o[k]=val0;
      if(opts){ d.innerHTML="<label for='"+id+k+"'>"+lab+"</label><span></span><select id='"+id+k+"'>"+opts.map((t,i)=>"<option value='"+i+"'>"+t+"</option>").join("")+"</select>";
        d.querySelector("select").addEventListener("change",e=>{o[k]=+e.target.value; maj();}); }
      else { d.innerHTML="<label for='"+id+k+"'>"+lab+"</label><output for='"+id+k+"'>"+fmt(val0)+"</output><input type='range' id='"+id+k+"' min='"+mn+"' max='"+mx+"' step='"+pas+"' value='"+val0+"'>";
        const inp=d.querySelector("input"), ou=d.querySelector("output"); inp.addEventListener("input",()=>{o[k]=+inp.value; ou.textContent=fmt(o[k]); maj();}); }
      c.appendChild(d); });
    c.appendChild(out); function maj(){ try{ out.innerHTML=def.f(o); }catch(e){ out.textContent="Le simulateur n'a pas pu s'afficher."; } } maj();
  });
})();
</script>""".replace("__PFUT__", str(PFU).replace(".", ",")).replace("__PST__", str(PS).replace(".", ",")).replace("__PFU__", str(PFU)).replace("__PS__", str(PS))
