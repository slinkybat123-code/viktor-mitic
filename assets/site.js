/* Viktor Mitic — shared behaviour for every page */
(()=>{
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
  const EMAIL='info@artorwar.com';
  const FALLBACK="data:image/svg+xml;utf8,"+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect width="400" height="400" fill="#1a1612"/><text x="200" y="205" fill="#a39a8d" font-family="Georgia" font-size="16" text-anchor="middle">Image unavailable</text></svg>');

  /* broken image fallback */
  document.addEventListener('error',e=>{const t=e.target;if(t.tagName==='IMG'&&t.src!==FALLBACK)t.src=FALLBACK},true);

  /* screen-reader cue on links that open a new tab */
  $$('a[target=_blank]').forEach(a=>{const s=document.createElement('span');s.className='sr';s.textContent=' (opens in a new tab)';a.appendChild(s)});

  /* navigation */
  const nav=$('#nav'),burger=$('#burger'),links=$('#links');
  if(nav){
    const onScroll=()=>nav.classList.toggle('solid',scrollY>60);
    addEventListener('scroll',onScroll,{passive:true});onScroll();
    const root=document.documentElement;
    const setMenu=o=>{links.classList.toggle('open',o);burger.setAttribute('aria-expanded',o);burger.textContent=o?'Close':'Menu';
      root.classList.toggle('menu-open',o);root.style.overflow=o?'hidden':''};
    const closeMenu=()=>{if(links.classList.contains('open'))setMenu(false)};
    burger.onclick=()=>{const o=!links.classList.contains('open');setMenu(o);if(o)$('a',links).focus({preventScroll:true})};
    matchMedia('(max-width:1100px)').addEventListener('change',e=>{if(!e.matches)closeMenu()});
    links.addEventListener('click',e=>{if(e.target.closest('a'))closeMenu()});
    addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(links.classList.contains('open')){closeMenu();burger.focus()}$$('.dd.open').forEach(d=>d.classList.remove('open'))});
    document.addEventListener('click',e=>{if(links.classList.contains('open')&&!nav.contains(e.target))closeMenu();
      $$('.dd.open').forEach(d=>{if(!d.contains(e.target))d.classList.remove('open')})});
    $$('.dd-btn').forEach(b=>b.onclick=()=>{const o=b.parentElement.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  }

  /* reveal on scroll */
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.06,rootMargin:'0px 0px -4% 0px'});
  $$('.rv').forEach(el=>io.observe(el));

  /* lightbox: any button with data-lb="group" */
  const lb=$('#lb');
  if(lb){
    const img=$('img',lb),ttl=$('.meta strong',lb),cap=$('.meta span',lb),enq=$('.meta a',lb),BLANK=img.src;
    let set=[],cur=0,opener=null;
    const show=i=>{cur=(i+set.length)%set.length;const b=set[cur];img.src=b.dataset.src;
      img.alt=b.dataset.alt||b.dataset.title||'Artwork by Viktor Mitic';
      ttl.textContent=b.dataset.title||'';cap.textContent=b.dataset.cap||'';
      if(b.dataset.enq){enq.hidden=false;enq.href=b.dataset.enq}else enq.hidden=true};
    document.addEventListener('click',e=>{const b=e.target.closest('[data-lb]');if(!b||b.dataset.dragged)return;
      set=$$('[data-lb="'+b.dataset.lb+'"]').filter(x=>!x.closest('[hidden]'));opener=b;
      show(Math.max(0,set.indexOf(b)));document.documentElement.style.overflow='hidden';lb.showModal()});
    $('.x',lb).onclick=()=>lb.close();
    $('.p',lb).onclick=()=>show(cur-1);
    $('.n',lb).onclick=()=>show(cur+1);
    lb.addEventListener('click',e=>{if(e.target===lb||e.target.classList.contains('lb'))lb.close()});
    lb.addEventListener('close',()=>{document.documentElement.style.overflow='';img.src=BLANK;opener&&opener.focus()});
    lb.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(cur-1);if(e.key==='ArrowRight')show(cur+1)});
    let tx=0,ty=0;
    lb.addEventListener('touchstart',e=>{const t=e.changedTouches[0];tx=t.clientX;ty=t.clientY},{passive:true});
    lb.addEventListener('touchend',e=>{const t=e.changedTouches[0],dx=t.clientX-tx,dy=t.clientY-ty;
      if(set.length>1&&Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)show(cur+(dx<0?1:-1))},{passive:true});
  }

  /* drag a strip with the mouse */
  $$('.strip').forEach(strip=>{
    let down=false,sx=0,sl=0,moved=false;
    $$('img',strip).forEach(i=>i.draggable=false);
    strip.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0)return;down=true;moved=false;sx=e.clientX;sl=strip.scrollLeft});
    addEventListener('pointermove',e=>{if(!down)return;const d=e.clientX-sx;if(Math.abs(d)>5){moved=true;strip.style.scrollSnapType='none'}strip.scrollLeft=sl-d});
    const end=()=>{if(!down)return;down=false;strip.style.scrollSnapType='';setTimeout(()=>moved=false,0)};
    addEventListener('pointerup',end);addEventListener('pointercancel',end);addEventListener('blur',end);
    strip.addEventListener('click',e=>{if(moved){e.stopPropagation();e.preventDefault()}},true);
  });

  /* landing hero: parallax and rain */
  const hi=$('#heroImg');
  if(hi&&!reduce)addEventListener('scroll',()=>{if(scrollY<innerHeight)hi.style.translate='0 '+(scrollY*.18)+'px'},{passive:true});
  const cv=$('#rain');
  if(cv&&!reduce){
    const ctx=cv.getContext('2d');let w=0,h=0,r=1,drops=[],raf=0,last=0;
    const size=()=>{r=Math.min(devicePixelRatio||1,2);const nw=Math.round(cv.clientWidth*r),nh=Math.round(cv.clientHeight*r);
      if(nw===w&&Math.abs(nh-h)<120*r)return;w=cv.width=nw;h=cv.height=nh;
      drops=Array.from({length:Math.min(140,Math.round(cv.clientWidth/9))},()=>({x:Math.random()*w,y:Math.random()*h,l:(10+Math.random()*22)*r,v:(9+Math.random()*10)*r,a:.15+Math.random()*.35}))};
    size();addEventListener('resize',size);
    const step=t=>{const k=Math.min((t-(last||t))/16.67,3);last=t;ctx.clearRect(0,0,w,h);ctx.lineWidth=r;
      for(const d of drops){ctx.strokeStyle='rgba(235,225,205,'+d.a+')';ctx.beginPath();ctx.moveTo(d.x,d.y);ctx.lineTo(d.x-d.l*.18,d.y+d.l);ctx.stroke();
        d.y+=d.v*k;d.x-=d.v*.18*k;if(d.y>h){d.y=-d.l;d.x=Math.random()*w+h*.18}}
      raf=requestAnimationFrame(step)};
    new IntersectionObserver(([e])=>{cancelAnimationFrame(raf);last=0;if(e.isIntersecting)raf=requestAnimationFrame(step)}).observe(cv);
  }

  /* cursor ring, fine pointers only */
  const ring=$('#ring');
  if(ring&&matchMedia('(hover:hover) and (pointer:fine)').matches&&!reduce){
    let x=0,y=0,tx=0,ty=0,run=false,first=true;
    const loop=()=>{x+=(tx-x)*.18;y+=(ty-y)*.18;ring.style.transform='translate('+x+'px,'+y+'px)';
      if(Math.abs(tx-x)+Math.abs(ty-y)>.1)requestAnimationFrame(loop);else run=false};
    addEventListener('mousemove',e=>{tx=e.clientX;ty=e.clientY;if(first){x=tx;y=ty;first=false}ring.classList.add('on');if(!run){run=true;requestAnimationFrame(loop)}},{passive:true});
    document.documentElement.addEventListener('mouseleave',()=>ring.classList.remove('on'));
    document.addEventListener('mouseover',e=>ring.classList.toggle('big',!!e.target.closest('a,button')));
  }

  /* available work: category filter */
  const filters=$('.filters');
  if(filters){
    const works=$$('.work'),count=$('#count');
    const apply=f=>{let n=0;works.forEach(w=>{const on=f==='all'||w.dataset.cat===f;w.hidden=!on;if(on)n++});
      $$('.chip',filters).forEach(c=>c.setAttribute('aria-pressed',c.dataset.filter===f));
      if(count)count.textContent='Showing '+n+' of '+works.length+' works'};
    filters.addEventListener('click',e=>{const c=e.target.closest('.chip');if(c){apply(c.dataset.filter);history.replaceState(null,'',c.dataset.filter==='all'?location.pathname:'#'+c.dataset.filter)}});
    const start=location.hash.slice(1);apply($('.chip[data-filter="'+start+'"]',filters)?start:'all');
  }

  /* video: load the player only when asked */
  document.addEventListener('click',e=>{const b=e.target.closest('button[data-yt],button[data-vimeo]');if(!b)return;
    const f=document.createElement('iframe');
    f.src=b.dataset.yt?'https://www.youtube-nocookie.com/embed/'+b.dataset.yt+'?autoplay=1&rel=0':'https://player.vimeo.com/video/'+b.dataset.vimeo+'?autoplay=1&dnt=1';
    f.title=b.getAttribute('aria-label').replace(/^Play:\s*/,'');f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;
    b.replaceWith(f);f.focus()});

  /* print button on the CV */
  $$('[data-print]').forEach(b=>b.onclick=()=>print());

  /* 3D turntable: a grid of rendered frames named {tilt}_{turn}.webp, loaded as they are needed */
  const turn=$('#turn');
  if(turn){
    const img=$('img',turn),note=$('.turn-load',turn),tabs=$$('.tabs .chip'),name=$('#viewerName'),EMPTY=img.src;
    let cfg={u:1,v:1,folder:''},u=0,v=0,cache={},want='';
    const wrap=(n,m)=>((n%m)+m)%m;
    const frame=(uu,vv)=>{const k=cfg.folder+'/'+vv+'_'+uu;
      if(!cache[k]){const im=new Image();im.decoding='async';im.src=turn.dataset.base+encodeURIComponent(cfg.folder)+'/'+vv+'_'+uu+'.webp';cache[k]=im}
      return cache[k]};
    const paint=()=>{const im=frame(u,v),k=im.src;want=k;
      const done=()=>{if(want===k){img.src=k;note.hidden=true}};
      if(im.complete&&im.naturalWidth)done();
      else{note.hidden=false;note.textContent='Loading…';im.addEventListener('load',done,{once:true});
        im.addEventListener('error',()=>{if(want===k)note.textContent='This view could not be loaded.'},{once:true})}
      [1,-1].forEach(d=>frame(wrap(u+d,cfg.u),v))};
    const pick=id=>{const t=tabs.find(x=>x.dataset.id===id)||tabs[0],d=t.dataset;
      tabs.forEach(x=>x.setAttribute('aria-pressed',x===t));
      cfg={folder:d.folder,u:+d.u,v:+d.v};u=+d.su;v=+d.sv;img.src=EMPTY;
      turn.style.aspectRatio=d.w+'/'+d.h;turn.style.maxWidth=d.w+'px';
      turn.setAttribute('aria-label','3D view of '+d.name+'. Drag, or use the arrow keys, to rotate.');
      if(name)name.textContent=d.name;paint()};
    let down=false,sx=0,sy=0,su=0,sv=0;
    turn.addEventListener('pointerdown',e=>{if(e.button)return;down=true;sx=e.clientX;sy=e.clientY;su=u;sv=v;turn.setPointerCapture(e.pointerId);turn.classList.add('grab');e.preventDefault()});
    turn.addEventListener('pointermove',e=>{if(!down)return;
      const nu=wrap(su-Math.round((e.clientX-sx)/(turn.clientWidth/cfg.u/1.4)),cfg.u),nv=wrap(sv+Math.round((e.clientY-sy)/(turn.clientHeight/cfg.v/1.2)),cfg.v);
      if(nu!==u||nv!==v){u=nu;v=nv;paint()}});
    const up=()=>{down=false;turn.classList.remove('grab')};
    turn.addEventListener('pointerup',up);turn.addEventListener('pointercancel',up);
    turn.addEventListener('keydown',e=>{const m={ArrowLeft:[1,0],ArrowRight:[-1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];if(!m)return;
      e.preventDefault();u=wrap(u+m[0],cfg.u);v=wrap(v+m[1],cfg.v);paint()});
    tabs.forEach(t=>t.onclick=()=>{pick(t.dataset.id);history.replaceState(null,'','#'+t.dataset.id)});
    pick(location.hash.slice(1));
  }

  /* copy the studio email address */
  const copy=async(text,statusEl,msg)=>{
    let ok=false;
    try{await navigator.clipboard.writeText(text);ok=true}catch(_){
      const t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();
      try{ok=document.execCommand('copy')}catch(_){}t.remove()}
    if(statusEl)statusEl.textContent=ok?msg:'Could not copy automatically. The address is '+EMAIL+'.';
  };
  $$('[data-copy-email]').forEach(b=>b.onclick=()=>copy(EMAIL,$('#'+b.dataset.copyEmail),'Address copied: '+EMAIL));

  /* contact form: writes the email, then hands it to the visitor's mail service */
  const form=$('#enquiry');
  if(form){
    const f=n=>form.elements[n],send=$('#send'),status=$('#formStatus');
    const q=new URLSearchParams(location.search);
    if(q.get('work')){f('ref').value=q.get('work').slice(0,80);f('topic').value='Available work'}
    else if(q.get('topic')){const o=[...f('topic').options].find(o=>o.value===q.get('topic'));if(o)f('topic').value=o.value}
    const setErr=(n,msg)=>{const el=f(n);el.setAttribute('aria-invalid',msg?'true':'false');$('#err-'+n).textContent=msg||''};
    const build=()=>{
      const ref=f('ref').value.trim(),topic=f('topic').value;
      const subject='Enquiry: '+topic+(ref?' ('+ref+')':'');
      const body=f('message').value.trim()+'\n\n'+f('name').value.trim()+'\n'+f('email').value.trim()+(ref?'\nWork: '+ref:'');
      return {subject,body};
    };
    form.addEventListener('submit',e=>{
      e.preventDefault();let bad=null;
      const need=(n,test,msg)=>{const ok=test(f(n).value.trim());setErr(n,ok?'':msg);if(!ok&&!bad)bad=f(n)};
      need('name',v=>v.length>1,'Please enter your name.');
      need('email',v=>/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v),'Please enter a valid email address.');
      need('message',v=>v.length>4,'Please write a short message.');
      if(bad){send.hidden=true;status.textContent='';bad.focus();return}
      const {subject,body}=build(),s=encodeURIComponent(subject),b=encodeURIComponent(body),to=encodeURIComponent(EMAIL);
      $('#viaGmail').href='https://mail.google.com/mail/?view=cm&fs=1&to='+to+'&su='+s+'&body='+b;
      $('#viaOutlook').href='https://outlook.live.com/mail/0/deeplink/compose?to='+to+'&subject='+s+'&body='+b;
      $('#viaYahoo').href='https://compose.mail.yahoo.com/?to='+to+'&subject='+s+'&body='+b;
      $('#viaApp').href='mailto:'+EMAIL+'?subject='+s+'&body='+b;
      $('#copyMsg').onclick=()=>copy('To: '+EMAIL+'\nSubject: '+subject+'\n\n'+body,status,'Message copied. Paste it into an email to '+EMAIL+'.');
      send.hidden=false;status.textContent='Your message is ready. Choose how to send it.';
      send.scrollIntoView({block:'nearest',behavior:reduce?'auto':'smooth'});$('#viaGmail').focus({preventScroll:true});
    });
    form.addEventListener('input',e=>{if(e.target.name&&e.target.getAttribute('aria-invalid')==='true')setErr(e.target.name,'');send.hidden=true});
  }
})();
