const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,Table,TableRow,TableCell,
       WidthType,ShadingType,AlignmentType,BorderStyle,PageBreak,TableOfContents,
       LevelFormat,convertInchesToTwip}=require('docx');

const TW=9360; // ширина таблицы в DXA (6.5")
function runs(text){
  // **жирный** и `код`
  const out=[]; const re=/(\*\*[^*]+\*\*|`[^`]+`)/g; let last=0,m;
  while((m=re.exec(text))!==null){
    if(m.index>last) out.push(new TextRun({text:text.slice(last,m.index)}));
    const t=m[0];
    if(t.startsWith('**')) out.push(new TextRun({text:t.slice(2,-2),bold:true}));
    else out.push(new TextRun({text:t.slice(1,-1),font:'Consolas',size:19}));
    last=m.index+t.length;
  }
  if(last<text.length) out.push(new TextRun({text:text.slice(last)}));
  return out.length?out:[new TextRun({text:''})];
}
function mdTable(lines){
  const rows=lines.filter(l=>!/^\s*\|[\s:|-]+\|\s*$/.test(l))
    .map(l=>l.trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim()));
  if(!rows.length) return null;
  const n=Math.max(...rows.map(r=>r.length));
  const cw=Array(n).fill(Math.floor(TW/n));
  return new Table({
    columnWidths:cw, width:{size:TW,type:WidthType.DXA},
    rows:rows.map((r,ri)=>new TableRow({
      tableHeader:ri===0,
      children:Array.from({length:n},(_,ci)=>new TableCell({
        width:{size:cw[ci],type:WidthType.DXA},
        shading:ri===0?{type:ShadingType.CLEAR,fill:'1F3864'}:
                (ri%2?{type:ShadingType.CLEAR,fill:'F2F5FB'}:undefined),
        margins:{top:60,bottom:60,left:100,right:100},
        children:[new Paragraph({spacing:{before:20,after:20},
          children:(r[ci]||'').split('**').map((t,i)=>new TextRun({
            text:t,bold:ri===0||i%2===1,color:ri===0?'FFFFFF':undefined,size:19}))})]
      }))
    }))
  });
}
function parse(md){
  const out=[]; const L=md.split('\n');
  for(let i=0;i<L.length;i++){
    const l=L[i];
    if(/^\s*\|/.test(l)){
      const blk=[]; while(i<L.length && /^\s*\|/.test(L[i])) blk.push(L[i++]); i--;
      const t=mdTable(blk); if(t){out.push(t); out.push(new Paragraph({text:'',spacing:{after:160}}));}
      continue;
    }
    if(/^---+$/.test(l.trim())){
      out.push(new Paragraph({text:'',border:{bottom:{style:BorderStyle.SINGLE,size:6,color:'C6CFE2'}},
                              spacing:{before:80,after:200}})); continue;
    }
    let m;
    if((m=l.match(/^(#{1,4})\s+(.*)$/))){
      const lvl=[HeadingLevel.HEADING_1,HeadingLevel.HEADING_2,HeadingLevel.HEADING_3,HeadingLevel.HEADING_4][m[1].length-1];
      out.push(new Paragraph({heading:lvl,children:runs(m[2]),
        spacing:{before:m[1].length===1?320:260,after:120}})); continue;
    }
    if((m=l.match(/^###\s+(.*)$/))){ out.push(new Paragraph({heading:HeadingLevel.HEADING_3,children:runs(m[1])})); continue; }
    if((m=l.match(/^\s*[-*]\s+(.*)$/))){
      out.push(new Paragraph({children:runs(m[1]),bullet:{level:0},spacing:{after:80}})); continue;
    }
    if((m=l.match(/^\s*(\d+)\.\s+(.*)$/))){
      out.push(new Paragraph({children:runs(m[2]),numbering:{reference:'num',level:0},spacing:{after:80}})); continue;
    }
    if(l.trim()==='') { continue; }
    // склеиваем подряд идущие строки в ОДИН абзац: в markdown перенос строки внутри
    // абзаца — это не новый абзац, а просто ширина колонки
    const buf=[l.trim()];
    while(i+1<L.length){
      const nx=L[i+1];
      if(nx.trim()==='' || /^\s*\|/.test(nx) || /^---+$/.test(nx.trim())
         || /^#{1,4}\s/.test(nx) || /^\s*[-*]\s/.test(nx) || /^\s*\d+\.\s/.test(nx)) break;
      buf.push(nx.trim()); i++;
    }
    out.push(new Paragraph({children:runs(buf.join(' ')),spacing:{after:140},
                            alignment:AlignmentType.JUSTIFIED}));
  }
  return out;
}

const final=fs.readFileSync('work/out/00_ФИНАЛ.md','utf8');
const method=fs.readFileSync('work/out/02_метод.md','utf8');

const doc=new Document({
  creator:'Анализ рынка Узбекистана',
  title:'Какой бизнес строить в Узбекистане',
  numbering:{config:[{reference:'num',levels:[{level:0,format:LevelFormat.DECIMAL,text:'%1.',
    alignment:AlignmentType.START,style:{paragraph:{indent:{left:convertInchesToTwip(0.4),hanging:convertInchesToTwip(0.22)}}}}]}]},
  styles:{default:{document:{run:{font:'Calibri',size:21},paragraph:{spacing:{line:276}}}},
    paragraphStyles:[
      {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,
       run:{size:34,bold:true,color:'1F3864',font:'Calibri'}},
      {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,
       run:{size:27,bold:true,color:'1F3864',font:'Calibri'}},
      {id:'Heading3',name:'Heading 3',basedOn:'Normal',next:'Normal',quickFormat:true,
       run:{size:23,bold:true,color:'2E4E8F',font:'Calibri'}},
      {id:'Heading4',name:'Heading 4',basedOn:'Normal',next:'Normal',quickFormat:true,
       run:{size:21,bold:true,color:'2E4E8F',font:'Calibri'}},
    ]},
  sections:[{
    properties:{page:{size:{width:11906,height:16838},margin:{top:1134,bottom:1134,left:1134,right:1134}}},
    children:[
      ...parse(final),
      new Paragraph({children:[new PageBreak()]}),
      ...parse(method),
    ]
  }]
});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('Узбекистан_выбор_бизнеса.docx',b);
  console.log('docx создан, байт:',b.length);});
