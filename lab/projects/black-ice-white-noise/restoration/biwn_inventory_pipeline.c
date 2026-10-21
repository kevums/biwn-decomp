#include "biwn_inventory_pipeline.h"
#include "biwn_text.h"
#include "biwn_gpu_commands.h"

struct pipeline_state {
    struct biwn_inventory_pipeline_bus *bus;
    enum biwn_inventory_pipeline_result error;
    const char *money;
};

static int budget(struct pipeline_state *state)
{
    if (state->error!=BIWN_PIPELINE_OK) return 1;
    if (!state->bus->read_budget) { state->error=BIWN_PIPELINE_READ_LIMIT;return 1; }
    state->bus->read_budget--;return 0;
}

static int read_byte(void *context,uint32_t address,uint8_t *value)
{
    struct pipeline_state *state=context;
    /* Internal alias for the private money string, not a game RAM mapping.
     * The preserved image uses font4C3E0 and local text at this call. */
    if (state->money && address>=0xffffffe0u) {
        *value=(uint8_t)state->money[address-0xffffffe0u];return 0;
    }
    if (budget(state)) return 1;
    if (state->bus->read8(state->bus->context,address,value)) { state->error=BIWN_PIPELINE_BUS_ERROR;return 1; }
    return 0;
}

static int read_word(void *context,uint32_t address,uint16_t *value)
{
    struct pipeline_state *state=context;
    if (budget(state)) return 1;
    if (state->bus->read16(state->bus->context,address,value)) { state->error=BIWN_PIPELINE_BUS_ERROR;return 1; }
    return 0;
}

static int read_long(void *context,uint32_t address,uint32_t *value)
{
    struct pipeline_state *state=context;
    if (budget(state)) return 1;
    if (state->bus->read32(state->bus->context,address,value)) { state->error=BIWN_PIPELINE_BUS_ERROR;return 1; }
    return 0;
}

static int write_long(void *context,uint32_t address,uint32_t value)
{
    struct pipeline_state *state=context;
    if (state->error!=BIWN_PIPELINE_OK) return 1;
    if (state->bus->write32(state->bus->context,address,value)) { state->error=BIWN_PIPELINE_BUS_ERROR;return 1; }
    return 0;
}

static int sprite(void *context,uint32_t base,uint32_t index,uint32_t destination)
{
    struct pipeline_state *state=context;
    struct biwn_gpu_bus bus={read_long,write_long,state,UINT32_MAX};
    enum biwn_gpu_result result=biwn_gpu_submit_4b00(&bus,base,index,destination);
    if (result!=BIWN_GPU_OK && state->error==BIWN_PIPELINE_OK) state->error=BIWN_PIPELINE_DEPENDENCY_ERROR;
    return result!=BIWN_GPU_OK;
}

static int text(void *context,const struct biwn_inventory_text *request)
{
    struct pipeline_state *state=context;
    struct biwn_text_bus bus={read_byte,read_word,write_long,state,UINT32_MAX};
    struct biwn_text_args args;
    uint32_t d0;
    enum biwn_text_result result;
    args.x=request->x;args.y=request->y;args.text=request->local_text ? 0xffffffe0u : request->text_address;
    args.target=request->target;args.target_flags=request->target_flags;args.font=request->font;
    args.color=request->color;args.mode=request->mode;
    state->money=request->local_text;result=biwn_text_draw(&bus,&args,&d0);state->money=0;
    if (result!=BIWN_TEXT_OK && state->error==BIWN_PIPELINE_OK) state->error=BIWN_PIPELINE_DEPENDENCY_ERROR;
    return result!=BIWN_TEXT_OK;
}

enum biwn_inventory_pipeline_result biwn_inventory_pipeline(struct biwn_inventory_pipeline_bus *bus)
{
    struct pipeline_state state;
    struct biwn_inventory_draw_bus draw;
    enum biwn_inventory_draw_result result;
    if (!bus || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write32) return BIWN_PIPELINE_BAD_ARGUMENT;
    state.bus=bus;state.error=BIWN_PIPELINE_OK;state.money=0;
    draw.read8=read_byte;draw.read16=read_word;draw.read32=read_long;draw.write32=write_long;
    draw.sprite=sprite;draw.text=text;draw.context=&state;
    result=biwn_inventory_draw(&draw);
    if (state.error!=BIWN_PIPELINE_OK) return state.error;
    return result==BIWN_DRAW_OK ? BIWN_PIPELINE_OK : BIWN_PIPELINE_DEPENDENCY_ERROR;
}
