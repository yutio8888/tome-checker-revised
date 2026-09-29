/* Maze materials use the validated Kor'Pul wall mask geometry and sampler. */
#define main korpul_export_main
#include "export_korpul_terrain.c"
#undef main

int main(int argc,char **argv){
 if(argc!=5)die("usage: export_maze_terrain KORPUL_MASTERS MAZE_MASTERS OUT REVIEW");
 floors[0]=readpng(argv[1],"floor-a-v2");
 floors[1]=readpng(argv[1],"floor-b-v2");
 tops[0]=readpng(argv[2],"old-lichen-wall-top-v1");
 blocks[0]=readpng(argv[2],"old-lichen-wall-edge-v1");
 Img chasm=readpng(argv[2],"maze-chasm-wide-v1");
 mkdir(argv[3],0755);mkdir(argv[4],0755);
 char path[2048];int count=0;
 for(int kind=0;kind<2;kind++)for(int mask=0;mask<(kind==0?16:1);mask++)for(int parity=0;parity<2;parity++){
  Img out;
  if(kind==0)out=render(2,mask,parity);
  else {
   out=blank(128);blit(out,chasm,whole(chasm),(Rect){0,0,128,128});
   if(parity)for(int i=0;i<128*128;i++)for(int c=0;c<3;c++)out.p[i*4+c]=(unsigned char)lround(out.p[i*4+c]*.90);
  }
  const char *name=kind==0?"old-wall":"cracks";
  snprintf(path,sizeof path,"%s/%s-%d-%d.png",argv[3],name,mask,parity);writepng(path,out);count++;
  const int sizes[]={48,64,96};for(int k=0;k<3;k++){
   snprintf(path,sizeof path,"%s/%d",argv[4],sizes[k]);mkdir(path,0755);
   Img sm=resize(out,sizes[k]);snprintf(path,sizeof path,"%s/%d/%s-%d-%d.png",argv[4],sizes[k],name,mask,parity);writepng(path,sm);free(sm.p);
  }free(out.p);
 }
 printf("%d Maze 128px RGBA runtime tiles\n",count);return count==34?0:1;
}
