document.addEventListener("DOMContentLoaded",()=>{

const canvas=document.createElement("canvas")
canvas.id="atmosphere"
canvas.style.position="fixed"
canvas.style.top="0"
canvas.style.left="0"
canvas.style.zIndex="-1"
document.body.appendChild(canvas)

const ctx=canvas.getContext("2d")

let w,h
function resize(){
w=canvas.width=window.innerWidth
h=canvas.height=window.innerHeight
}
resize()
window.addEventListener("resize",resize)

let mouseX=0
let mouseY=0
window.addEventListener("mousemove",e=>{
mouseX=e.clientX/w
mouseY=e.clientY/h
})

let t=0

const thunderSound=new Audio("/styles/lightning_sound.mp3")
thunderSound.volume=0.3
thunderSound.preload="auto"

document.addEventListener("click",()=>{
thunderSound.play().then(()=>{
thunderSound.pause()
thunderSound.currentTime=0
}).catch(()=>{})
},{once:true})

function noise(x,y){
return(
Math.sin(x*0.01)+
Math.sin(y*0.01)+
Math.sin((x+y)*0.008)+
Math.sin((x-y)*0.012)
)/4
}

let stars=[]
for(let i=0;i<200;i++){
stars.push({x:Math.random()*w,y:Math.random()*h,z:Math.random()*2})
}

let sparks=[]
for(let i=0;i<90;i++){
sparks.push({x:Math.random()*w,y:Math.random()*h,s:Math.random()*2,v:Math.random()*0.5+0.1})
}

function drawStars(){
stars.forEach(s=>{
let px=s.x+mouseX*60*s.z
let py=s.y+mouseY*60*s.z
ctx.fillStyle="rgba(255,255,255,0.7)"
ctx.fillRect(px,py,s.z,s.z)
})
}

function drawNebula(){
const size=60
for(let x=0;x<w;x+=size){
for(let y=0;y<h;y+=size){
let n=noise(x+t*40,y+t*30)
if(n>0){
ctx.fillStyle=`rgba(120,180,255,${n*0.07})`
ctx.fillRect(x,y,size,size)
}
}}
}

function drawAurora(){
let g=ctx.createLinearGradient(0,h*0.2+Math.sin(t*0.5)*160,w,h)
g.addColorStop(0,"rgba(0,255,200,0.15)")
g.addColorStop(0.25,"rgba(120,0,255,0.15)")
g.addColorStop(0.5,"rgba(0,120,255,0.15)")
g.addColorStop(0.75,"rgba(0,255,160,0.15)")
g.addColorStop(1,"rgba(0,255,200,0.12)")
ctx.fillStyle=g
ctx.fillRect(0,0,w,h)
}

function drawSparks(){
sparks.forEach(p=>{
p.y-=p.v
if(p.y<0){
p.y=h
p.x=Math.random()*w
}

let o=Math.sin((p.y+t)*0.05)*0.5+0.5

ctx.beginPath()
ctx.arc(p.x,p.y,p.s,0,Math.PI*2)
ctx.fillStyle=`rgba(255,40,60,${o})`
ctx.fill()

if(Math.random()<0.004){
ctx.beginPath()
ctx.arc(p.x,p.y,p.s*4,0,Math.PI*2)
ctx.fillStyle="rgba(255,0,0,0.9)"
ctx.fill()
thunderSound.play().catch(()=>{})
}
})
}

function drawPulse(){
if(Math.sin(t*0.6)>0.985){
let g=ctx.createRadialGradient(w/2,h/2,0,w/2,h/2,800)
g.addColorStop(0,"rgba(255,0,70,0.2)")
g.addColorStop(1,"transparent")
ctx.fillStyle=g
ctx.fillRect(0,0,w,h)
}
}

function drawGrid(){
ctx.strokeStyle="rgba(255,255,255,0.02)"
ctx.lineWidth=1

for(let x=0;x<w;x+=80){
ctx.beginPath()
ctx.moveTo(x,0)
ctx.lineTo(x,h)
ctx.stroke()
}

for(let y=0;y<h;y+=80){
ctx.beginPath()
ctx.moveTo(0,y)
ctx.lineTo(w,y)
ctx.stroke()
}
}

function animate(){
ctx.clearRect(0,0,w,h)
t+=0.01
drawStars()
drawNebula()
drawAurora()
drawSparks()
drawPulse()
drawGrid()
requestAnimationFrame(animate)
}

animate()

})
