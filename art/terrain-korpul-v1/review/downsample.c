/* Mechanical sprite export only. Creature artwork and native alpha are from
 * ImageGen. No colour changes, background removal, invented detail or rings.
 * Preserve the whole square canvas and downsample
 * with a premultiplied-alpha area filter. Preserve original masters separately.
 * Build: cc -O2 tools/export_token.c -o tools/bin/export_token -lpng -lm
 */
#include <png.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static void fail(const char *message) { fprintf(stderr, "%s\n", message); exit(1); }
int main(int argc, char **argv) {
    if (argc != 4) fail("usage: export_token INPUT.png OUTPUT.png SIZE");
    char *end = NULL;
    long size = strtol(argv[3], &end, 10);
    if (*end || size < 16 || size > 1024) fail("SIZE must be 16..1024");
    png_image src = {0}; src.version = PNG_IMAGE_VERSION;
    if (!png_image_begin_read_from_file(&src, argv[1])) fail(src.message);
    if (src.width > 8192 || src.height > 8192) fail("unexpected master dimensions");
    src.format = PNG_FORMAT_RGBA;
    unsigned char *pixels = malloc(PNG_IMAGE_SIZE(src));
    if (!pixels) fail("out of memory");
    if (!png_image_finish_read(&src, NULL, pixels, 0, NULL)) fail(src.message);
    int x0 = src.width, y0 = src.height, x1 = -1, y1 = -1;
    unsigned long transparent = 0;
    for (int y = 0; y < (int)src.height; ++y) for (int x = 0; x < (int)src.width; ++x) {
        int a = pixels[((size_t)y * src.width + x) * 4 + 3];
        if (a == 0) ++transparent;
        /* Ignore near-invisible alpha noise for measuring bounds ONLY.
         * The sampling pass preserves alpha values inside the export window. */
        if (a > 8) {
            if (x < x0) x0 = x;
            if (x > x1) x1 = x;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
        }
    }
    if (src.width != src.height) fail("review expects square master");
    double extent = src.width;
    double left = 0, top = 0;
    double step = extent / size;
    unsigned char *out = calloc((size_t)size * size, 4);
    if (!out) fail("out of memory");
    for (int y = 0; y < size; ++y) for (int x = 0; x < size; ++x) {
        double l = left + x * step, r = l + step;
        double t = top + y * step, b = t + step;
        double rgba[4] = {0, 0, 0, 0};
        for (int yy = (int)floor(t); yy < (int)ceil(b); ++yy) {
            if (yy < 0 || yy >= (int)src.height) continue;
            double wy = fmin(b, yy + 1) - fmax(t, yy);
            for (int xx = (int)floor(l); xx < (int)ceil(r); ++xx) {
                if (xx < 0 || xx >= (int)src.width) continue;
                double weight = wy * (fmin(r, xx + 1) - fmax(l, xx));
                unsigned char *p = pixels + ((size_t)yy * src.width + xx) * 4;
                double aw = p[3] * weight;
                for (int c = 0; c < 3; ++c) rgba[c] += p[c] * aw;
                rgba[3] += aw;
            }
        }
        unsigned char *p = out + ((size_t)y * size + x) * 4;
        p[3] = (unsigned char)fmin(255, lround(rgba[3] / (step * step)));
        if (p[3]) for (int c = 0; c < 3; ++c)
            p[c] = (unsigned char)fmin(255, lround(rgba[c] / rgba[3]));
    }
    png_image dst = {0}; dst.version = PNG_IMAGE_VERSION;
    dst.width = dst.height = size; dst.format = PNG_FORMAT_RGBA;
    if (!png_image_write_to_file(&dst, argv[2], 0, out, 0, NULL)) fail(dst.message);
    printf("{\"size\":%ld,\"master_width\":%u,\"master_height\":%u,\"visible_bbox\":[%d,%d,%d,%d],\"export_window\":[%.6f,%.6f,%.6f],\"target_occupancy\":1.0}\n",
           size, src.width, src.height, x0, y0, x1+1, y1+1, left, top, extent);
    free(pixels); free(out); png_image_free(&src); png_image_free(&dst);
    return 0;
}
