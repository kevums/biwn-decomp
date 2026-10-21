#ifndef BIWN_MOVIE_VBI_EVENT_H
#define BIWN_MOVIE_VBI_EVENT_H
#include "biwn_video_cpu.h"
/* Controlled VBI at the source movie-dispatch boundary D4A8. Pushes the
 * real six-byte supervisor IRQ2 frame and reads vector100. Source E7D4/RTE
 * executes separately. Caller supplies shared TOM pending-video event.
 * Masked IRQ leaves CPU unchanged. Other errors preserve input CPU with
 * earlier bus writes retained. No timing/firmware/global scheduler claim. */
int biwn_movie_VBI_event(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
