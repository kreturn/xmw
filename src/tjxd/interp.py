#############################################################################
"""
Demo of dynamic warping for automatic picking
Author: Xinming Wu, University of Texas at Austin
Version: 2016.06.01
"""


from utils3 import * 
setupForSubset("full")
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count
f1,f2,f3 = s1.getFirst(),s2.getFirst(),s3.getFirst()
d1,d2,d3 = s1.getDelta(),s2.getDelta(),s3.getDelta()
l1,l2,l3 = s1.last,s2.last,s3.last
#############################################################################
gxfile = "gx" # input semblance image
gmfile = "gm" # mask image
pxfile = "px" # image-guided nearest interpolation
qxfile = "qx" # image-guided blended interpolation
txfile = "tx" # image-guided distance
exfile = "ex" # tensors
exsfile = "exs" #scaled tensors
s1file = "sx1"
s2file = "sx2"
s3file = "sx3"
sxfile = "sx"
epfile = "ep"  # planarity
effile = "ef"  # 1-planarity
fefile = "fe"  # 1-planarity
fpfile = "fp"  # fault strike;
ftfile = "ft"  # fault dip;
fvfile = "fv"  # fault dip;
ftfile  = "ft" # fault dip (theta)
fetfile = "fet" # fault likelihood thinned
fptfile = "fpt" # fault likelihood thinned
fttfile = "ftt" # fault dip thinned
vpfile = "vp"
vtfile = "vt"
epvfile = "epv"


pngDir = getPngDir()
pngDir = None
plotOnly = True
# These parameters control the scan over fault strikes and dips.
# See the class FaultScanner for more information.
minTheta,maxTheta = 65,80
minPhi,maxPhi = 0,360
sigmaPhi,sigmaTheta=4,8
background = Color.WHITE

c2s = [670916,660065,659116,664891,661082,677668,
       676790,677017,682230,676987,671153,672222]	

c3s = [4530909,4532272,4533012,4532232,4530130,4533492,
       4531236,4533302,4533286,4532326,4529709,4530982]

wns =["YC1","YJ1-3","YJ1-5","YJ1-9X","YJ1X","YJ2-3","YJ2-7X",
      "YJ2-9","YJ2X","YJ3","YJ3-2","YJ3-3H"]
logDir = "../../../data/seis/tjxd/3d/logs/las/"
dvtDir = "../../../data/seis/tjxd/3d/logs/dvt/"
logType = "velocity"



def main(args):
  #gridWellLogs(logType)
  goDisplay()
  #goMaskImage()
  #goTensors()
  #goSemblance()
  #scaleTensors(0.001)
  #goImageGuidedInterp()
  #goFaultLikelihood()
  #goPlanar()
  #goFaultOrientScan()
  #goSurfaceVoting()
  #goFvPlanar()
  #showSub1()
  #showSub2()
  #showSub3()
  #goSkins()

def goImageGuidedInterp():
  ex = readTensors(exsfile)
  bi = BlendedGridder3(ex)
  px = readImage3D("wg"+logType[0])
  tx = bi.gridNearest(0.0,px)
  writeImage(pxfile,px)
  writeImage(txfile,tx)
  bg.setSmoothness(1.0)
  tx = clip(0.0,50.0,tx)
  qx = copy(px)
  bg.gridBlended(tx,px,qx)
  writeImage(qxfile,qx)
  '''
  plot3(gx,qx,cmin=2,cmax=6.0,cmap=jetRamp(1.0),
      clab="Velocity",png="qx")
  '''

def gridWellLogs(logType):
  fnull = 0.0
  wlg = WellLogGridder(s1,s2,s3,fnull)
  fx,x1,x2,x3=getLogSamples(logType)
  print logType+"min =",min(fx)," max =",max(fx)
  wlg.insertWellLog(fx,x1,x2,x3)
  g = wlg.getGriddedValues()
  gfile = "wg"+logType[0]
  writeImage(gfile,g)
  samples = fx,x1,x2,x3
  plot3(g)
  plot3(g,samples=samples)

def goDisplay():
  gx = readImage3D(gxfile)
  gx = gain(gx)
  fk,k1,k2,k3=getLogSamples("velocity")
  samples = fk,k1,k2,k3
  plot3(gx,samples=samples)

def goMaskImage():
  gx = readImage3D(gxfile)
  mask = ZeroMask(0.1,10.0,1.0,1.0,gx)
  gm = mask.getAsFloats()
  writeImage(gmfile,gm)

def goTensors():
  sigma = 8.0
  gx = readImage3D(gxfile)
  gm = readImage3D(gmfile)
  mask = ZeroMask(gm)
  lof = LocalOrientFilter(sigma)
  ex = lof.applyForTensors(gx)
  mask.apply((1.0,0.0,0.0,1.0,0.0,1.0),ex)
  writeTensors(exfile,ex)

def scaleTensors(eps):
  ex = readTensors(exfile)
  sx1 = readImage3D(s1file); print "sx1 min =",min(sx1)," max =",max(sx1)
  sx2 = readImage3D(s2file); print "sx2 min =",min(sx2)," max =",max(sx2)
  sx3 = readImage3D(s3file); print "sx3 min =",min(sx3)," max =",max(sx3)
  pow(sx2,4.0,sx2)
  fill(eps,sx3)
  sx1 = clip(eps,1.0,sx1)
  sx2 = clip(eps,1.0,sx2)
  sx3 = clip(eps,1.0,sx3)
  ex.setEigenvalues(sx3,sx2,sx1)
  writeTensors(exsfile,ex)

def goSemblance():
  mask = ZeroMask(readImage3D(gmfile))
  '''
  semblance1(mask)
  semblance2(mask)
  semblance3(mask)
  '''
  for smfile in [s1file,s2file,s3file]:
    sm = readImage3D(smfile)
    if smfile==s3file:
      mask.apply(0.0001,sm)
    else:
      mask.apply(1.00,sm)
    writeImage(smfile,sm)

def semblance1(mask):
  lsf1 = LocalSemblanceFilter(2,2)
  ex = readTensors(exfile)
  gx = readImage3D(gxfile)
  sx1 = lsf1.semblance(LocalSemblanceFilter.Direction3.W,ex,gx)
  mask.apply(1.00,sx1)
  writeImage(s1file,sx1)

def semblance2(mask):
  lsf2 = LocalSemblanceFilter(2,8)
  ex = readTensors(exfile)
  gx = readImage3D(gxfile)
  sx2 = lsf2.semblance(LocalSemblanceFilter.Direction3.VW,ex,gx)
  mask.apply(1.00,sx2)
  writeImage(s2file,sx2)

def semblance3(mask):
  lsf3 = LocalSemblanceFilter(16,0)
  ex = readTensors(exfile)
  gx = readImage3D(gxfile)
  sx3 = lsf3.semblance(LocalSemblanceFilter.Direction3.UVW,ex,gx)
  mask.apply(0.01,sx3)
  writeImage(s3file,sx3)


def getLogSamples(curve):
  k1,k2,k3,fk=[],[],[],[]
  wldata = WellLog.Data(logDir, dvtDir)
  logs = wldata.getLogsWith(curve)
  wi = 0
  for log in logs:
    print log.name
    c2,c3 = getLogLocation(log.name)
    print c2
    print c3
    fxs = log.getSamplesX(curve)
    if(fxs!=None):
      fx = fxs[0]
      x1 = fxs[1]
      if(fx!=None and x1!=None):
        for k in range(len(fx)):
          fk.append(fx[k])
          k1.append(x1[k])
          k2.append(c2)
          k3.append(c3)
  return fk,k1,k2,k3

def getLogLocation(name):
  wi = 0
  for wni in wns:
    if(wni==name):
      return c2s[wi],c3s[wi]
    wi = wi+1

def goFaultLikelihood():
  minPhi,maxPhi = 0,360
  minTheta,maxTheta = 80,88
  sigmaPhi,sigmaTheta = 12,40
  gx = readImage3D(gxfile)
  gx = gain(gx)
  if not plotOnly:
    sigma1,sigma2,sigma3,pmax = 16.0,1.0,1.0,5.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
    gx = FaultScanner.taper(10,0,0,gx)
    fs = FaultScanner(sigmaPhi,sigmaTheta)
    fl,fp,ft = fs.scan(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gx)
    print "fl min =",min(fl)," max =",max(fl)
    print "fp min =",min(fp)," max =",max(fp)
    print "ft min =",min(ft)," max =",max(ft)
    writeImage(flfile,fl)
    writeImage(fpfile,fp)
    writeImage(ftfile,ft)
  else:
    fl = readImage3D(flfile)
  plot3(gx,fl,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Fault likelihood",png="fl")

def goPlanar():
  gx = readImage3D(gxfile)
  if not plotOnly:
    lof = LocalOrientFilter(16,4)
    et3 = lof.applyForTensors(gx)
    et3.setEigenvalues(1.0,0.01,0.5)
    fer = FaultEnhancer(sigmaPhi,sigmaTheta)
    ep = fer.applyForPlanar(10,et3,gx)
    writeImage(epfile,ep)
    print min(ep)
    print max(ep)
  else:
    ep = readImage3D(epfile)
  #plot3(gx,cmin=-3,cmax=3)
  #plot3(ep,cmin=0.2,cmax=1.0,clab="Planarity",cint=0.1)
  ep = pow(ep,6)
  plot3(gx,sub(1,ep),cmin=0.1,cmax=0.8,cmap=jetRamp(1.0),
      clab="1-planarity",png="fl")

def goFaultOrientScan():
  gx = readImage3D(gxfile)
  ep = readImage3D(epfile)
  fos = FaultOrientScanner3(sigmaPhi,sigmaTheta)
  if not plotOnly:
    fe,fp,ft = fos.scan(minPhi,maxPhi,minTheta,maxTheta,ep)
    fet,fpt,ftt=fos.thin([fe,fp,ft])
    writeImage(fefile,fe)
    writeImage(fpfile,fp)
    writeImage(fetfile,fet)
    writeImage(fptfile,fpt)
    writeImage(fttfile,ftt)
  else:
    fp = readImage3D(fpfile)
    fe = readImage3D(fefile)
  print min(fe) 
  print max(fe) 
  plot3(gx,ep,cmin=0.1,cmax=0.7,cmap=jetRamp(1.0),
      clab="1-planarity",png="ep")
  plot3(gx,fe,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Enhanced",png="fe")
  plot3(gx,fp,cmin=1,cmax=360,cmap=jetFill(1.0),
      clab="Fault strike (degrees)",png="fp")

def goSurfaceVoting():
  gx = readImage3D(gxfile)
  if not plotOnly:
    fet = readImage3D(fetfile)
    fpt = readImage3D(fptfile)
    ftt = readImage3D(fttfile)
    osv = OptimalSurfaceVoterP(10,30,20)
    osv.setStrainMax(0.2,0.2)
    osv.setSurfaceSmoothing(2,2)
    #fv = osv.applyVoting(4,0.3,fet,fpt,ftt)
    fv,vp,vt = osv.applyVoting(4,0.3,fet,fpt,ftt)
    writeImage("vp",vp)
    writeImage("vt",vt)
    #writeImage(fvfile,fv)
  else:
    fv = readImage3D(fvfile)
  ep = readImage3D(epfile)
  ep = sub(1,pow(ep,8))
  plot3(gx,ep,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="1-planarity",png="ep")
  plot3(gx,fv,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Surface voting",png="sv")

def showSub1():
  gx = readImage3D(gxfile)
  osv = OptimalSurfaceVoterP(10,20,30)
  fv = readImage3D(fvfile)
  vp = readImage3D(vpfile)
  vt = readImage3D(vtfile)
  ep = readImage3D(epvfile)
  gx = copy(n1,410,500,0,510,324,gx)
  fv = copy(n1,410,500,0,510,324,fv)
  vp = copy(n1,410,500,0,510,324,vp)
  vt = copy(n1,410,500,0,510,324,vt)
  ep = copy(n1,410,500,0,510,324,ep)
  ft,pt,tt = osv.thin([fv,vp,vt])
  '''
  fsk = FaultSkinner()
  seeds = fsk.findSeeds(10,0.8,ep,ft,pt,tt)
  skins = fsk.findSkins(0.7,20000,seeds,fv,vp,vt)
  for skin in skins:
    skin.smooth(5)
  plot3(gx,au=140,skinx=skins)
  '''
  plot3(gx,au=140,png="sub1/seis")
  plot3(gx,fv,au=140,cmin=0.3,cmax=1.0,cmap=jetRamp(1.0),
      clab="Voting score",png="sub1/fv")
  plot3(gx,ft,au=140,cmin=0.3,cmax=0.9,cmap=jetRamp(1.0),
      clab="Voting score",png="sub1/fvt")
def showSub2():
  gx = readImage3D(gxfile)
  osv = OptimalSurfaceVoterP(10,20,30)
  fv = readImage3D(fvfile)
  vp = readImage3D(vpfile)
  vt = readImage3D(vtfile)
  ep = readImage3D(epvfile)
  gx = copy(n1,360,500,0,150,324,gx)
  fv = copy(n1,360,500,0,150,324,fv)
  vp = copy(n1,360,500,0,150,324,vp)
  vt = copy(n1,360,500,0,150,324,vt)
  ep = copy(n1,360,500,0,150,324,ep)
  ft,pt,tt = osv.thin([fv,vp,vt])
  '''
  fsk = FaultSkinner()
  seeds = fsk.findSeeds(10,0.8,ep,ft,pt,tt)
  skins = fsk.findSkins(0.7,20000,seeds,fv,vp,vt)
  for skin in skins:
    skin.smooth(5)
  plot3(gx,au=140,skinx=skins)
  '''
  plot3(gx,au=140)
  plot3(gx,fv,au=140,cmin=0.3,cmax=1.0,cmap=jetRamp(1.0),
      clab="Surface voting",png="fe")
  plot3(gx,ft,au=140,cmin=0.3,cmax=1.0,cmap=jetFillExceptMin(1.0),
      clab="Surface voting",png="fe")

def showSub3():
  gx = readImage3D(gxfile)
  osv = OptimalSurfaceVoterP(10,20,30)
  fv = readImage3D(fvfile)
  vp = readImage3D(vpfile)
  vt = readImage3D(vtfile)
  ep = readImage3D(epvfile)
  gx = copy(n1,410,500,0,510,0,gx)
  fv = copy(n1,410,500,0,510,0,fv)
  vp = copy(n1,410,500,0,510,0,vp)
  vt = copy(n1,410,500,0,510,0,vt)
  ep = copy(n1,410,500,0,510,0,ep)
  ft,pt,tt = osv.thin([fv,vp,vt])
  '''
  fsk = FaultSkinner()
  seeds = fsk.findSeeds(10,0.8,ep,ft,pt,tt)
  skins = fsk.findSkins(0.7,20000,seeds,fv,vp,vt)
  for skin in skins:
    skin.smooth(5)
  plot3(gx,au=140,skinx=skins)
  '''
  plot3(gx,au=140,k2=330,png="sub3/seis")
  plot3(gx,fv,au=140,k2=330,cmin=0.3,cmax=1.0,cmap=jetRamp(1.0),
      clab="Voting score",png="sub3/fv")
  plot3(gx,ft,au=140,k2=330,cmin=0.3,cmax=0.9,cmap=jetRamp(1.0),
      clab="Voting score",png="sub3/fvt")
  plot3f(gx,k2=330,png="sub3/seisf")
  plot3f(gx,a=ft,k2=330,amin=0.3,amax=1.0,png="sub3/fvtf")

def goSkins():
  gx = readImage3D(gxfile)
  osv = OptimalSurfaceVoterP(10,20,30)
  fv = readImage3D(fvfile)
  vp = readImage3D(vpfile)
  vt = readImage3D(vtfile)
  ep = readImage3D(epvfile)
  '''
  gx = copy(n1,400,500,0,100,224,gx)
  fv = copy(n1,400,500,0,100,224,fv)
  vp = copy(n1,400,500,0,100,224,vp)
  vt = copy(n1,400,500,0,100,224,vt)
  ep = copy(n1,400,500,0,100,224,ep)
  '''
  '''
  gx = copy(n1,410,500,0,100,324,gx)
  ft = copy(n1,410,500,0,100,324,ft)
  plot3(gx,ft,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
      clab="Surface voting",png="fe")

  '''
  '''
  gx = copy(n1,410,500,0,510,324,gx)
  fv = copy(n1,410,500,0,510,324,fv)
  vp = copy(n1,410,500,0,510,324,vp)
  vt = copy(n1,410,500,0,510,324,vt)
  ep = copy(n1,410,500,0,510,324,ep)
  '''
  gx = copy(n1,410,500,0,510,0,gx)
  vp = copy(n1,410,500,0,510,0,vp)
  vt = copy(n1,410,500,0,510,0,vt)
  fv = copy(n1,410,500,0,510,0,fv)
  ep = copy(n1,410,500,0,510,0,ep)
  ft,pt,tt = osv.thin([fv,vp,vt])
  plot3(gx,clab="Amplitude",png="seis")
  '''
  plot3(gx,ft,cmin=0.25,cmax=1.0,cmap=jetFillExceptMin(1.0),
      clab="Surface voting",png="fe")
  fsk = FaultSkinner()
  fsk.setGrowing(10,0.1)
  seeds = fsk.findSeeds(10,0.7,ep,ft,pt,tt)
  skins = fsk.findSkins(0.5,2000,seeds,fv,vp,vt)
  for skin in skins:
    skin.smooth(5)
  for skin in skins:
    skin.updateStrike()
  plot3(gx,fv,au=140,k2=330,cmin=0.25,cmax=1.0,cmap=jetRamp(1.0),
      clab="Surface voting",png="fe")
  plot3(gx,au=140,k2=330,skinx=skins, png="skinSub3")
  '''
def goFvPlanar():
  fv = readImage3D(fvfile)
  u1 = zerofloat(n1,n2,n3)
  u2 = zerofloat(n1,n2,n3)
  u3 = zerofloat(n1,n2,n3)
  ep = zerofloat(n1,n2,n3)
  lof = LocalOrientFilter(4,2,2)
  lof.applyForNormalPlanar(fv,u1,u2,u3,ep)
  writeImage(epvfile,ep)

def gain(x):
  g = mul(x,x) 
  ref = RecursiveExponentialFilter(100.0)
  ref.apply1(g,g)
  y = zerofloat(n1,n2,n3)
  div(x,sqrt(g),y)
  return y
def normalize(e):
  emin = min(e)
  emax = max(e)
  return mul(sub(e,emin),1.0/(emax-emin))

#############################################################################
# graphics

def jetFill(alpha):
  return ColorMap.setAlpha(ColorMap.JET,alpha)
def jetFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.JET,a)
def jetRamp(alpha):
  return ColorMap.setAlpha(ColorMap.JET,rampfloat(0.0,alpha/256,256))
def bwrFill(alpha):
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,alpha)
def bwrNotch(alpha):
  a = zerofloat(256)
  for i in range(len(a)):
    if i<128:
      a[i] = alpha*(128.0-i)/128.0
    else:
      a[i] = alpha*(i-127.0)/128.0
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,a)
def hueFill(alpha):
  return ColorMap.getHue(0.0,1.0,alpha)
def hueFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.getHue(0.0,1.0),a)

def addColorBar(frame,clab=None,cint=None):
  cbar = ColorBar(clab)
  if cint:
    cbar.setInterval(cint)
  cbar.setFont(Font("Arial",Font.PLAIN,24)) # size by experimenting
  cbar.setWidthMinimum
  cbar.setBackground(Color.WHITE)
  frame.add(cbar,BorderLayout.EAST)
  return cbar

def convertDips(ft):
  return FaultScanner.convertDips(0.2,ft) # 5:1 vertical exaggeration

def makePointGroup(f,x1,x2,x3,cmin,cmax,cbar):
  n = len(x1)
  xyz = zerofloat(3*n)
  copy(n,0,1,x3,0,3,xyz)
  copy(n,0,1,x2,1,3,xyz)
  copy(n,0,1,x1,2,3,xyz)
  rgb = None
  if cmin<cmax:
    cmap = ColorMap(cmin,cmax,ColorMap.getJet(1.0))
    if cbar:
      cmap.addListener(cbar)
    rgb = cmap.getRgbFloats(f)
  pg = PointGroup(xyz,rgb)
  ps = PointState()
  ps.setSize(12)
  ps.setSmooth(False)
  ss = StateSet()
  ss.add(ps)
  pg.setStates(ss)
  return pg

def plot3(f,g=None,k1=120,k2=298,k3=39,au=300,cmin=-2,cmax=2,
          cmap=None,clab=None,cint=None,cells=None,samples=None,skinx=None,png=None):
  n3 = len(f)
  n2 = len(f[0])
  n1 = len(f[0][0])
  '''
  s1,s2,s3=Sampling(n1),Sampling(n2),Sampling(n3)
  d1,d2,d3 = s1.delta,s2.delta,s3.delta
  f1,f2,f3 = s1.first,s2.first,s3.first
  l1,l2,l3 = s1.last,s2.last,s3.last
  '''
  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  cbar = None
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-2.0,2.0)
    if clab:
      cbar = addColorBar(sf,clab,cint)
      ipg.addColorMapListener(cbar)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-2,2)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    if clab:
      cbar = addColorBar(sf,clab,0.1)
      ipg.addColorMap2Listener(cbar)
    sf.world.addChild(ipg)
  if cbar:
    cbar.setWidthMinimum(85)
  if samples:
    fx,x1,x2,x3 = samples
    vmin,vmax,vmap= min(fx),max(fx),ColorMap.JET
    pg = makePointGroup(fx,x1,x2,x3,vmin,vmax,None)
    sf.world.addChild(pg)
  if cells:
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    cmap = ColorMap(0.0,1.0,ColorMap.JET)
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.7,cmap,cells,False)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if skinx:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    lms.setTwoSide(False)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    sg.setStates(ss)
    for skin in skinx:
      #cmap = ColorMap(0.25,1.0,ColorMap.JET)
      cmap = ColorMap(0,180,ColorMap.JET)
      qg = skin.getQuadMeshStrike(cmap)
      sg.addChild(qg)
    sf.world.addChild(sg)
  ipg.setSlices(k1,k2,k3)
  if cbar:
    sf.setSize(1051,750)
  else:
    sf.setSize(950,750)
  view = sf.getOrbitView()
  zscale = 0.5*max(n2*d2,n3*d3)/(n1*d1)
  view.setAxesScale(1.0,1.0,zscale)
  view.setScale(1.6)
  view.setAzimuth(au)
  view.setElevation(35)
  view.setWorldSphere(BoundingSphere(BoundingBox(f3,f2,f1,l3,l2,l1)))
  view.setTranslate(Vector3(0.02,-0.02,0.1))
  sf.viewCanvas.setBackground(sf.getBackground())
  sf.setVisible(True)
  if png and pngDir:
    sf.paintToFile(pngDir+png+".png")
    if cbar:
      cbar.paintToPng(720,1,pngDir+png+"cbar.png")

def plot3f(g,a=None,k1=120,k2=298,k3=39,amin=None,amax=None,
          amap=jetRamp(1.0),alab="Voting score",aint=0.1, png=None):
  n3 = len(g)
  n2 = len(g[0])
  n1 = len(g[0][0])
  s1 = Sampling(n1)
  s2 = Sampling(n2)
  s3 = Sampling(n3)
  pp = PlotPanelPixels3(
    PlotPanelPixels3.Orientation.X1DOWN_X2RIGHT,
    PlotPanelPixels3.AxesPlacement.LEFT_BOTTOM,
    s1,s2,s3,g)
  pp.setSlices(k1,k2,k3)
  pp.setLabel1("Depth (sample)")
  pp.setLabel2("Inline (trace)")
  pp.setLabel3("Crossline (trace)")
  pp.mosaic.setHeightElastic(1,120)
  pp.setClips(-2,2)
  if a:
    pp.setLineColor(Color.WHITE)
    cb = pp.addColorBar(alab)
    if aint:
      cb.setInterval(aint)
  else:
    pp.setLineColor(Color.WHITE)
    cb = pp.addColorBar("Amplitude")
    cb.setInterval(2.0)
  pp.setInterval1(50)
  pp.setInterval2(50)
  pp.setInterval3(50)
  if a:
    pv12 = PixelsView(s1,s2,slice12(k3,a))
    pv12.setOrientation(PixelsView.Orientation.X1DOWN_X2RIGHT)
    pv12.setInterpolation(PixelsView.Interpolation.NEAREST)
    pv13 = PixelsView(s1,s3,slice13(k2,a))
    pv13.setOrientation(PixelsView.Orientation.X1DOWN_X2RIGHT)
    pv13.setInterpolation(PixelsView.Interpolation.NEAREST)
    pv23 = PixelsView(s2,s3,slice23(k1,a))
    pv23.setOrientation(PixelsView.Orientation.X1RIGHT_X2UP)
    pv23.setInterpolation(PixelsView.Interpolation.NEAREST)
    for pv in [pv12,pv13,pv23]:
      pv.setColorModel(amap)
      if amin!=amax:
        pv.setClips(amin,amax)
    pp.pixelsView12.tile.addTiledView(pv12)
    pp.pixelsView13.tile.addTiledView(pv13)
    pp.pixelsView23.tile.addTiledView(pv23)
  pf = PlotFrame(pp)
  pf.setBackground(background)
  pp.setColorBarWidthMinimum(65)
  pf.setFontSize(16)
  pf.setSize(1000,700)
  pf.setVisible(True)
  if png and pngDir:
    pf.paintToPng(360,7.0,pngDir+png+".png")

def slice12(k3,f):
  n1,n2,n3 = len(f[0][0]),len(f[0]),len(f)
  s = zerofloat(n1,n2)
  SimpleFloat3(f).get12(n1,n2,0,0,k3,s)
  return s

def slice13(k2,f):
  n1,n2,n3 = len(f[0][0]),len(f[0]),len(f)
  s = zerofloat(n1,n3)
  SimpleFloat3(f).get13(n1,n3,0,k2,0,s)
  return s

def slice23(k1,f):
  n1,n2,n3 = len(f[0][0]),len(f[0]),len(f)
  s = zerofloat(n2,n3)
  SimpleFloat3(f).get23(n2,n3,k1,0,0,s)
  return s

#############################################################################
# Run the function main on the Swing thread
import sys
class _RunMain(Runnable):
  def __init__(self,main):
    self.main = main
  def run(self):
    self.main(sys.argv)
def run(main):
  SwingUtilities.invokeLater(_RunMain(main)) 
run(main)
