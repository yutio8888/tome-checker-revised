/* Deterministic assembly of ImageGen-painted terrain components, not painting.
 * All RGB detail comes from preserved masters. Operations: rectangle masks,
 * area resampling, alpha-over, fixed parity modulation and in-cell grid edge.
 * No rotation, noise, background extraction or invented stone/wood texture.
 * cc -O2 tools/export_korpul_terrain.c -o /tmp/export_korpul_terrain -lpng -lm
 * Run from addon root: BIN art/terrain-korpul-v1/masters data/gfx/refined/korpul
 *                         art/terrain-korpul-v1/review/runtime
 */
#include <png.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/stat.h>

typedef struct {int w,h; unsigned char *p;} Img;
typedef struct {double x0,y0,x1,y1;} Rect;
static Img floors[2], tops[2], blocks[2], leafh, leafv;
static const char *names[]={"floor-a","floor-b","wall","hardwall","door-closed-horizontal","door-closed-vertical","door-open-horizontal","door-open-vertical"};
static void die(const char *s){fprintf(stderr,"%s\n",s);exit(1);}
static Img readpng(const char *dir,const char *name){
 char p[2048];snprintf(p,sizeof p,"%s/%s.png",dir,name);
 png_image q={0};q.version=PNG_IMAGE_VERSION;
 if(!png_image_begin_read_from_file(&q,p))die(q.message);
 q.format=PNG_FORMAT_RGBA;Img im={(int)q.width,(int)q.height,malloc(PNG_IMAGE_SIZE(q))};
 if(!im.p||!png_image_finish_read(&q,NULL,im.p,0,NULL))die(q.message);
 png_image_free(&q);return im;
}
static void writepng(const char *p,Img im){png_image q={0};q.version=PNG_IMAGE_VERSION;q.width=im.w;q.height=im.h;q.format=PNG_FORMAT_RGBA;if(!png_image_write_to_file(&q,p,0,im.p,0,NULL))die(q.message);}
static Img blank(int n){Img im={n,n,calloc((size_t)n*n,4)};if(!im.p)die("allocation");return im;}
/* Exact premultiplied-alpha area filtering over source rectangle. */
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
/* dst coordinates use the fixed 128-world-pixel canvas. */
static void blit(Img dst,Img src,Rect crop,Rect box){
 double scale=dst.w/128.0;
 for(int y=(int)floor(box.y0*scale);y<(int)ceil(box.y1*scale);y++)for(int x=(int)floor(box.x0*scale);x<(int)ceil(box.x1*scale);x++){
  if(x<0||y<0||x>=dst.w||y>=dst.h)continue;
  double px0=fmax(x/scale,box.x0),px1=fmin((x+1)/scale,box.x1),py0=fmax(y/scale,box.y0),py1=fmin((y+1)/scale,box.y1);
  if(px1<=px0||py1<=py0)continue;
  double sx=(crop.x1-crop.x0)/(box.x1-box.x0),sy=(crop.y1-crop.y0)/(box.y1-box.y0),v[4];
  sample(src,crop.x0+(px0-box.x0)*sx,crop.y0+(py0-box.y0)*sy,crop.x0+(px1-box.x0)*sx,crop.y0+(py1-box.y0)*sy,v);
  v[3]*=(px1-px0)*(py1-py0)*scale*scale;over(dst.p+4*((size_t)y*dst.w+x),v);
 }
}
static Rect whole(Img im){return (Rect){0,0,im.w,im.h};}
/* Fixed world-facing crops from the original isolated ImageGen blocks.
 * N/W are their actual light-facing edge; S/E their original dark side.
 * These four strips are NEVER rotated or mirrored. */
static Rect edgecrop(int hard,int edge){
 static const Rect r[2][4]={
  {{135,132,1100,160},{1120,190,1170,1030},{140,1045,1120,1145},{89,180,128,1010}},
  {{140,101,1100,128},{1130,190,1172,1050},{140,1035,1110,1147},{83,190,122,1050}}
 };return r[hard][edge];
}
static void block(Img dst,int hard,Rect b,int connect){
 /* Material sampling is fixed in world coordinates, not stretched per mask. */
 Rect crop={b.x0/128*tops[hard].w,b.y0/128*tops[hard].h,b.x1/128*tops[hard].w,b.y1/128*tops[hard].h};
 blit(dst,tops[hard],crop,b);
 if(!(connect&1))blit(dst,blocks[hard],edgecrop(hard,0),(Rect){b.x0,b.y0,b.x1,b.y0+2});
 if(!(connect&8))blit(dst,blocks[hard],edgecrop(hard,3),(Rect){b.x0,b.y0,b.x0+2,b.y1});
 if(!(connect&2))blit(dst,blocks[hard],edgecrop(hard,1),(Rect){b.x1-5,b.y0+2,b.x1,b.y1});
 if(!(connect&4))blit(dst,blocks[hard],edgecrop(hard,2),(Rect){b.x0,b.y1-9,b.x1,b.y1});
}
static Img render(int kind,int mask,int parity){
 Img out=blank(128);int floor=kind<2?kind:0;blit(out,floors[floor],whole(floors[floor]),(Rect){0,0,128,128});
 /* In-cell printed grid, below objects. No line is placed on a connected cap. */
 for(int y=0;y<128;y++)for(int x=0;x<128;x++)if(x==0||y==0||x==127||y==127){unsigned char *p=out.p+4*(y*128+x);for(int c=0;c<3;c++)p[c]=(unsigned char)lround(p[c]*.88);}
 /* Walls occupy their whole rule cell; inset floor gutters would falsely look
  * traversable and would separate a wall from an adjoining door jamb. */
 if(kind==2||kind==3)block(out,kind==3,(Rect){0,0,128,128},mask);
 if(kind>=4){
  int vertical=kind==5||kind==7,open=kind>=6;
  if(!vertical){
   block(out,0,(Rect){(mask&8)?0:4,84,20,124},mask&8);
   block(out,0,(Rect){108,84,(mask&2)?128:124,124},mask&2);
   if(open)blit(out,leafv,(Rect){516,75,740,1177},(Rect){16,16,34,104});
   else blit(out,leafh,(Rect){89,517,1166,758},(Rect){19,96,109,116});
  }else{
   block(out,0,(Rect){4,(mask&1)?0:4,44,20},mask&1);
   block(out,0,(Rect){4,108,44,(mask&4)?128:124},mask&4);
   if(open)blit(out,leafh,(Rect){89,517,1166,758},(Rect){24,100,112,120});
   else blit(out,leafv,(Rect){516,75,740,1177},(Rect){16,19,34,109});
  }
 }
 /* Same deterministic board modulation for all materials; no recoloured master. */
 if(parity)for(int i=0;i<128*128;i++)for(int c=0;c<3;c++)out.p[i*4+c]=(unsigned char)lround(out.p[i*4+c]*.90);
 return out;
}
static Img resize(Img im,int n){Img o=blank(n);for(int y=0;y<n;y++)for(int x=0;x<n;x++){double v[4];sample(im,x*im.w/(double)n,y*im.h/(double)n,(x+1)*im.w/(double)n,(y+1)*im.h/(double)n,v);for(int c=0;c<4;c++)o.p[4*(y*n+x)+c]=(unsigned char)lround(v[c]);}return o;}
int main(int argc,char **argv){
 if(argc!=4)die("usage: export_korpul_terrain MASTERS OUT REVIEW");
 floors[0]=readpng(argv[1],"floor-a-v2");floors[1]=readpng(argv[1],"floor-b-v2");
 tops[0]=readpng(argv[1],"wall-top-v1");tops[1]=readpng(argv[1],"hardwall-top-v1");
 blocks[0]=readpng(argv[1],"wall-v1");blocks[1]=readpng(argv[1],"hardwall-v1");
 leafh=readpng(argv[1],"door-leaf-horizontal-v1");leafv=readpng(argv[1],"door-leaf-vertical-v2");
 mkdir(argv[2],0755);mkdir(argv[3],0755);char path[2048];int count=0;
 for(int kind=0;kind<8;kind++)for(int mask=0;mask<(kind<2?1:16);mask++)for(int parity=0;parity<2;parity++){
  Img out=render(kind,mask,parity);snprintf(path,sizeof path,"%s/%s-%d-%d.png",argv[2],names[kind],mask,parity);writepng(path,out);count++;
  const int sizes[]={48,64,96};for(int k=0;k<3;k++){snprintf(path,sizeof path,"%s/%d",argv[3],sizes[k]);mkdir(path,0755);Img sm=resize(out,sizes[k]);snprintf(path,sizeof path,"%s/%d/%s-%d-%d.png",argv[3],sizes[k],names[kind],mask,parity);writepng(path,sm);free(sm.p);}free(out.p);
 }
 printf("%d complete 128px RGBA runtime tiles, with 48/64/96 review downscales\n",count);return count==196?0:1;
}
