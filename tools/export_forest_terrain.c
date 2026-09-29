/* Deterministic assembly of forest/water terrain runtime tiles from masters.
 * Mirrors tools/export_korpul_terrain.c: no rotation, no noise, no invented
 * texture, no randomness. All RGB detail comes from preserved masters; the
 * only per-cell operations are area resampling, alpha-over compositing, a
 * fixed single-row/column grid-line darkening (N/W edge only, "below
 * objects"), directional bank blits for water shore, and a fixed parity
 * multiply applied last over the whole cell. C is used for the same reason
 * as the Kor'Pul exporter: floating point rounding must be bit-reproducible
 * across machines and the acceptance gates (A4-A6) compare exact bytes.
 *
 * Reverse-engineered constants (see docs/g0-terrain-contract-20260927/EXPORTER.md):
 *  - LINE_MULT  0.765  : median row0/row1 (and col0/col1) ratio measured on
 *                        grass0/road0/flower0/tree-oak0 in data/gfx/refined.
 *                        Applied only to the N row and W col, before props
 *                        and before any water bank blit (a bank blit, when
 *                        it happens, overwrites the darkened line -- this
 *                        matches deep0's bright N bank vs deep15's darker,
 *                        undarkened-bank N edge in the real assets).
 *  - PARITY_MULT 0.895  : ACCEPTANCE.md A4 declared k for the forest suite
 *                        (measured range 0.8947-0.8974 across grass/flower/
 *                        road/exit/tree-oak/tree-pine/tree-willow/bog/water,
 *                        plus deep0/bog5/deep15).
 *  - Mask bits: N=1 E=2 S=4 W=8, matching CheckerTerrain.lua's dirs order
 *    and ACCEPTANCE.md 2.2. A bit is 1 when that neighbour is the SAME
 *    rendering identity (no bank drawn on that edge).
 *
 * cc -O2 tools/export_forest_terrain.c -o /tmp/export_forest_terrain -lpng -lm
 *
 * Usage:
 *   export_forest_terrain MASTERS OUT REVIEW [F1_MASTERS F1_OUT]
 * MASTERS must contain (all square PNGs, any size >=128, resampled to 128):
 *   floor-grass.png floor-road.png floor-flower.png floor-deep.png floor-bog.png
 *   prop-tree-oak.png prop-tree-pine.png prop-tree-willow.png prop-exit.png
 *   bank-deep-N.png bank-deep-E.png bank-deep-S.png bank-deep-W.png
 *   bank-bog-N.png  bank-bog-E.png  bank-bog-S.png  bank-bog-W.png
 * OUT gets the real runtime-named tile set (safe to point at a scratch dir;
 * this tool never touches data/gfx itself -- the caller decides OUT).
 * If F1_MASTERS/F1_OUT are given, the F1 (flooded Trollmire) identities are
 * also rendered, from F1_MASTERS plus the bog floor/bank masters already
 * loaded from MASTERS, into F1_OUT (kept separate from OUT so a run can
 * never be mistaken for the main non-flooded set; the caller decides
 * whether F1_OUT is a scratch dir or points straight at data/gfx/refined/):
 *   prop-bog-tree-a.png, prop-bog-tree-b.png
 *                                       -> bog-tree-a<mask>-<parity>-0.png,
 *                                          bog-tree-b<mask>-<parity>-0.png (64)
 *   prop-bog-misc-1/2/3.png            -> bog-misc<1..3>-<parity>-0.png (6)
 *   (bog<mask>-<parity>-0.png itself is already proven by the main OUT run;
 *   F1_OUT does not re-emit it.)
 * prop-tree-hard.png in F1_MASTERS is OPTIONAL: if present, hardtree tiles
 * are also rendered (-> tree-hard<parity>.png, 2, grass-based like the other
 * TREE-family props, no water mask). If absent, hardtree stays uncovered and
 * native, same as any other not-yet-produced identity (see CONTRACT I1).
 */
#include <png.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/stat.h>

#define N 128
#define LINE_MULT 0.765
#define PARITY_MULT 0.895

typedef struct {int w,h; unsigned char *p;} Img;
typedef struct {double x0,y0,x1,y1;} Rect;
static void die(const char *s){fprintf(stderr,"%s\n",s);exit(1);}

static Img readpng(const char *dir,const char *name){
 char p[2048];snprintf(p,sizeof p,"%s/%s",dir,name);
 png_image q={0};q.version=PNG_IMAGE_VERSION;
 if(!png_image_begin_read_from_file(&q,p))die(q.message);
 q.format=PNG_FORMAT_RGBA;Img im={(int)q.width,(int)q.height,malloc(PNG_IMAGE_SIZE(q))};
 if(!im.p||!png_image_finish_read(&q,NULL,im.p,0,NULL))die(q.message);
 png_image_free(&q);return im;
}
static int exists(const char *dir,const char *name){
 char p[2048];snprintf(p,sizeof p,"%s/%s",dir,name);
 FILE *f=fopen(p,"rb");if(!f)return 0;fclose(f);return 1;
}
static void writepng(const char *p,Img im){png_image q={0};q.version=PNG_IMAGE_VERSION;q.width=im.w;q.height=im.h;q.format=PNG_FORMAT_RGBA;if(!png_image_write_to_file(&q,p,0,im.p,0,NULL))die(q.message);}
static Img blank(int n){Img im={n,n,calloc((size_t)n*n,4)};if(!im.p)die("allocation");return im;}

/* Exact premultiplied-alpha area filtering over a source rectangle, in the
 * source image's own pixel space (l,t,r,b are source coordinates). */
static void sample(Img im,double l,double t,double r,double b,double out[4]){
 double v[4]={0};double area=(r-l)*(b-t);
 for(int y=(int)floor(t);y<(int)ceil(b);y++){
  if(y<0||y>=im.h)continue;
  double wy=fmin(b,y+1)-fmax(t,y);
  for(int x=(int)floor(l);x<(int)ceil(r);x++){
   if(x<0||x>=im.w)continue;
   double w=wy*(fmin(r,x+1)-fmax(l,x));
   unsigned char *p=im.p+4*((size_t)y*im.w+x);double a=p[3]*w;
   for(int c=0;c<3;c++)v[c]+=p[c]*a;
   v[3]+=a;
  }
 }
 out[3]=area>0?v[3]/area:0;for(int c=0;c<3;c++)out[c]=v[3]>0?v[c]/v[3]:0;
}
static void over(unsigned char *dst,double src[4]){double a=src[3]/255.0,oa=a+dst[3]/255.0*(1-a);for(int c=0;c<3;c++)dst[c]=(unsigned char)lround(oa>0?(src[c]*a+dst[c]*dst[3]/255.0*(1-a))/oa:0);dst[3]=(unsigned char)lround(255*oa);}
/* dst coordinates use the fixed 128-world-pixel canvas; src is resampled to
 * fill box exactly (crop maps onto box). */
static void blit(Img dst,Img src,Rect crop,Rect box){
 for(int y=(int)floor(box.y0);y<(int)ceil(box.y1);y++)for(int x=(int)floor(box.x0);x<(int)ceil(box.x1);x++){
  if(x<0||y<0||x>=dst.w||y>=dst.h)continue;
  double px0=fmax((double)x,box.x0),px1=fmin((double)x+1,box.x1),py0=fmax((double)y,box.y0),py1=fmin((double)y+1,box.y1);
  if(px1<=px0||py1<=py0)continue;
  double sx=(crop.x1-crop.x0)/(box.x1-box.x0),sy=(crop.y1-crop.y0)/(box.y1-box.y0),v[4];
  sample(src,crop.x0+(px0-box.x0)*sx,crop.y0+(py0-box.y0)*sy,crop.x0+(px1-box.x0)*sx,crop.y0+(py1-box.y0)*sy,v);
  v[3]*=(px1-px0)*(py1-py0);over(dst.p+4*((size_t)y*dst.w+x),v);
 }
}
static Rect whole(Img im){return (Rect){0,0,im.w,im.h};}
static Img floor_to_128(Img master){Img out=blank(N);blit(out,master,whole(master),(Rect){0,0,N,N});return out;}
static void composite_prop(Img dst,Img prop){blit(dst,prop,whole(prop),(Rect){0,0,N,N});}

/* Single-row/col grid line, N and W edges only, drawn on the floor/water
 * before props and before any bank blit (a bank on an unset edge overwrites
 * it, matching the real assets: deep0's N bank is bright, deep15's N edge
 * -- no bank, water continues -- is darkened by this same line). */
static void grid_line(Img im){
 for(int x=0;x<im.w;x++){unsigned char *p=im.p+4*((size_t)0*im.w+x);for(int c=0;c<3;c++)p[c]=(unsigned char)lround(p[c]*LINE_MULT);}
 for(int y=0;y<im.h;y++){unsigned char *p=im.p+4*((size_t)y*im.w+0);for(int c=0;c<3;c++)p[c]=(unsigned char)lround(p[c]*LINE_MULT);}
}
static void parity_mult(Img im){for(int i=0;i<im.w*im.h;i++)for(int c=0;c<3;c++)im.p[i*4+c]=(unsigned char)lround(im.p[i*4+c]*PARITY_MULT);}

/* bank[0..3] = N,E,S,W crops, each spanning the full opposite dimension and
 * BANK_DEPTH deep into the cell from that edge. */
#define BANK_DEPTH 10
static void bank_blit(Img dst,Img bank[4],int mask){
 if(!(mask&1))blit(dst,bank[0],whole(bank[0]),(Rect){0,0,N,BANK_DEPTH});
 if(!(mask&2))blit(dst,bank[1],whole(bank[1]),(Rect){N-BANK_DEPTH,0,N,N});
 if(!(mask&4))blit(dst,bank[2],whole(bank[2]),(Rect){0,N-BANK_DEPTH,N,N});
 if(!(mask&8))blit(dst,bank[3],whole(bank[3]),(Rect){0,0,BANK_DEPTH,N});
}

static Img render_floor(Img master,int parity){
 Img out=floor_to_128(master);grid_line(out);if(parity)parity_mult(out);return out;
}
static Img render_prop_over_floor(Img floorMaster,Img prop,int parity){
 Img out=floor_to_128(floorMaster);grid_line(out);composite_prop(out,prop);if(parity)parity_mult(out);return out;
}
static Img render_daikara_wall(Img floorMaster,Img wall,int mask,int parity){
 Img out=floor_to_128(floorMaster);grid_line(out);
 /* The slab is one continuous block. Each set bit carries opaque material
  * from its top/face across the complete shared edge, underneath the slab.
  * Thus a neighboring wall touches rock, rather than two isolated props
  * separated by strips of visible floor. N/E/S/W match CheckerTerrain. */
 Rect top={wall.w*.25,wall.h*.25,wall.w*.75,wall.h*.40};
 Rect face={wall.w*.25,wall.h*.60,wall.w*.75,wall.h*.78};
 if(mask&1)blit(out,wall,top,(Rect){12,0,116,45});
 if(mask&2)blit(out,wall,face,(Rect){83,12,128,116});
 if(mask&4)blit(out,wall,face,(Rect){12,83,116,128});
 if(mask&8)blit(out,wall,face,(Rect){0,12,45,116});
 composite_prop(out,wall);if(parity)parity_mult(out);return out;
}
static Img render_water(Img floorMaster,Img bank[4],int mask,int parity){
 Img out=floor_to_128(floorMaster);grid_line(out);bank_blit(out,bank,mask);if(parity)parity_mult(out);return out;
}
static Img render_prop_over_water(Img floorMaster,Img bank[4],Img prop,int mask,int parity){
 Img out=floor_to_128(floorMaster);grid_line(out);bank_blit(out,bank,mask);composite_prop(out,prop);if(parity)parity_mult(out);return out;
}
static Img resize(Img im,int n){Img o=blank(n);for(int y=0;y<n;y++)for(int x=0;x<n;x++){double v[4];sample(im,x*im.w/(double)n,y*im.h/(double)n,(x+1)*im.w/(double)n,(y+1)*im.h/(double)n,v);for(int c=0;c<4;c++)o.p[4*(y*n+x)+c]=(unsigned char)lround(v[c]);}return o;}

static void emit(const char *outdir,const char *reviewdir,const char *name,Img out,int *count){
 char path[2048];
 if(outdir){snprintf(path,sizeof path,"%s/%s.png",outdir,name);writepng(path,out);}
 if(reviewdir){
  const int sizes[]={48,64,96};
  for(int k=0;k<3;k++){
   snprintf(path,sizeof path,"%s/%d",reviewdir,sizes[k]);mkdir(path,0755);
   Img sm=resize(out,sizes[k]);
   snprintf(path,sizeof path,"%s/%d/%s.png",reviewdir,sizes[k],name);writepng(path,sm);free(sm.p);
  }
 }
 (*count)++;
}

int main(int argc,char **argv){
 if(argc==6&&strcmp(argv[1],"--daikara")==0){
  const char *mdir=argv[2],*snowdir=argv[3],*outdir=argv[4],*reviewdir=argv[5];
  mkdir(outdir,0755);mkdir(reviewdir,0755);
  Img ground=readpng(mdir,"floor-bare-rock.png"),lava=readpng(mdir,"floor-harmless-lava.png");
  Img wall=readpng(mdir,"prop-mountain-wall.png");
  const char *propnames[]={"prop-snow-tree-pine.png","prop-snow-tree-elm.png",
   "prop-snow-exit-up.png","prop-snow-exit-down.png","prop-snow-exit-world.png"};
  const char *kinds[]={"tree-pine","tree-elm","stairs-up","stairs-down","stairs-world"};
  int count=0;char name[128];
  for(int parity=0;parity<2;parity++){
   Img o=render_floor(ground,parity);snprintf(name,sizeof name,"rock-ground%d",parity);
   emit(outdir,reviewdir,name,o,&count);free(o.p);
   o=render_floor(lava,parity);snprintf(name,sizeof name,"lava-floor%d",parity);
   emit(outdir,reviewdir,name,o,&count);free(o.p);
   for(int i=0;i<5;i++){
    Img prop=readpng(snowdir,propnames[i]);o=render_prop_over_floor(ground,prop,parity);
    snprintf(name,sizeof name,"%s%d",kinds[i],parity);
    emit(outdir,reviewdir,name,o,&count);free(o.p);free(prop.p);
   }
   for(int mask=0;mask<16;mask++){
    o=render_daikara_wall(ground,wall,mask,parity);
    snprintf(name,sizeof name,"mountain-wall-%d%d",mask,parity);
    emit(outdir,reviewdir,name,o,&count);free(o.p);
   }
  }
  free(ground.p);free(lava.p);free(wall.p);
  printf("daikara: %d runtime tiles\n",count);return 0;
 }
 if(argc==5&&strcmp(argv[1],"--snow")==0){
  const char *mdir=argv[2],*outdir=argv[3],*reviewdir=argv[4];
  mkdir(outdir,0755);mkdir(reviewdir,0755);
  Img ground=readpng(mdir,"floor-snow-ground.png");
  const char *propnames[]={"prop-snow-tree-pine.png","prop-snow-tree-elm.png",
   "prop-snow-exit-up.png","prop-snow-exit-down.png","prop-snow-exit-world.png"};
  const char *kinds[]={"tree-pine","tree-elm","stairs-up","stairs-down","stairs-world"};
  int count=0;char name[128];
  for(int parity=0;parity<2;parity++){
   Img o=render_floor(ground,parity);
   snprintf(name,sizeof name,"snow-ground%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
   for(int i=0;i<5;i++){
    Img prop=readpng(mdir,propnames[i]);
    o=render_prop_over_floor(ground,prop,parity);
    snprintf(name,sizeof name,"%s%d",kinds[i],parity);
    emit(outdir,reviewdir,name,o,&count);free(o.p);free(prop.p);
   }
  }
  free(ground.p);
  printf("snow: %d runtime tiles (floor, two blocking trees, three exits x parity)\n",count);
  return 0;
 }
 if(argc!=4&&argc!=6)die("usage: export_forest_terrain MASTERS OUT REVIEW [F1_MASTERS F1_OUT] | --snow MASTERS OUT REVIEW");
 const char *mdir=argv[1],*outdir=argv[2],*reviewdir=argv[3];
 mkdir(outdir,0755);mkdir(reviewdir,0755);
 Img grass=readpng(mdir,"floor-grass.png"),road=readpng(mdir,"floor-road.png"),flower=readpng(mdir,"floor-flower.png");
 Img treeOak=readpng(mdir,"prop-tree-oak.png"),treePine=readpng(mdir,"prop-tree-pine.png"),treeWillow=readpng(mdir,"prop-tree-willow.png"),exitProp=readpng(mdir,"prop-exit.png");
 Img deep=readpng(mdir,"floor-deep.png"),bog=readpng(mdir,"floor-bog.png");
 Img bankDeep[4]={readpng(mdir,"bank-deep-N.png"),readpng(mdir,"bank-deep-E.png"),readpng(mdir,"bank-deep-S.png"),readpng(mdir,"bank-deep-W.png")};
 Img bankBog[4]={readpng(mdir,"bank-bog-N.png"),readpng(mdir,"bank-bog-E.png"),readpng(mdir,"bank-bog-S.png"),readpng(mdir,"bank-bog-W.png")};
 int count=0;char name[128];

 for(int parity=0;parity<2;parity++){
  Img o;
  o=render_floor(grass,parity);snprintf(name,sizeof name,"grass%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_floor(road,parity);snprintf(name,sizeof name,"road%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_floor(flower,parity);snprintf(name,sizeof name,"flower%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_prop_over_floor(grass,treeOak,parity);snprintf(name,sizeof name,"tree-oak%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_prop_over_floor(grass,treePine,parity);snprintf(name,sizeof name,"tree-pine%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_prop_over_floor(grass,treeWillow,parity);snprintf(name,sizeof name,"tree-willow%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  o=render_prop_over_floor(grass,exitProp,parity);snprintf(name,sizeof name,"exit%d",parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  for(int mask=0;mask<16;mask++){
   o=render_water(deep,bankDeep,mask,parity);snprintf(name,sizeof name,"deep%d-%d-0",mask,parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
   o=render_water(bog,bankBog,mask,parity);snprintf(name,sizeof name,"bog%d-%d-0",mask,parity);emit(outdir,reviewdir,name,o,&count);free(o.p);
  }
 }
 printf("main: %d runtime tiles (grass/road/flower/exit/tree-oak/tree-pine/tree-willow x2 + deep/bog x16x2), LINE_MULT=%.3f PARITY_MULT=%.3f\n",count,LINE_MULT,PARITY_MULT);

 if(argc==6){
  const char *f1mdir=argv[4],*f1out=argv[5];
  mkdir(f1out,0755);
  Img bogTreeA=readpng(f1mdir,"prop-bog-tree-a.png");
  Img bogTreeB=readpng(f1mdir,"prop-bog-tree-b.png");
  Img misc[3];for(int i=0;i<3;i++){snprintf(name,sizeof name,"prop-bog-misc-%d.png",i+1);misc[i]=readpng(f1mdir,name);}
  int f1count=0;
  for(int parity=0;parity<2;parity++){
   for(int mask=0;mask<16;mask++){
    Img oa=render_prop_over_water(bog,bankBog,bogTreeA,mask,parity);
    snprintf(name,sizeof name,"bog-tree-a%d-%d-0",mask,parity);emit(f1out,NULL,name,oa,&f1count);free(oa.p);
    Img ob=render_prop_over_water(bog,bankBog,bogTreeB,mask,parity);
    snprintf(name,sizeof name,"bog-tree-b%d-%d-0",mask,parity);emit(f1out,NULL,name,ob,&f1count);free(ob.p);
   }
   for(int i=0;i<3;i++){
    Img o=render_prop_over_water(bog,bankBog,misc[i],0,parity);
    snprintf(name,sizeof name,"bog-misc%d-%d-0",i+1,parity);emit(f1out,NULL,name,o,&f1count);free(o.p);
   }
  }
  free(bogTreeA.p);free(bogTreeB.p);for(int i=0;i<3;i++)free(misc[i].p);
  printf("f1: %d tiles (bog-tree-a x16x2 + bog-tree-b x16x2 + bog-misc x3x2) written to %s\n",f1count,f1out);

  /* hardtree is optional: its master may not exist yet (blocked generation).
   * An uncovered identity stays native, same as any other not-yet-produced
   * one (CONTRACT I1); this exporter must not require it to run the rest
   * of F1. */
  if(exists(f1mdir,"prop-tree-hard.png")){
   Img treeHard=readpng(f1mdir,"prop-tree-hard.png");
   int hardcount=0;
   for(int parity=0;parity<2;parity++){
    Img o=render_prop_over_floor(grass,treeHard,parity);
    snprintf(name,sizeof name,"tree-hard%d",parity);emit(f1out,NULL,name,o,&hardcount);free(o.p);
   }
   free(treeHard.p);
   printf("f1: %d hardtree tile(s) written to %s\n",hardcount,f1out);
  } else {
   printf("f1: prop-tree-hard.png not found in %s, hardtree skipped (stays native)\n",f1mdir);
  }
 }
 return 0;
}
