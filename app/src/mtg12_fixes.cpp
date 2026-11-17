// Magic 2012 TU #3: shared-return compatibility hooks.
#include "generated/default/mtg12_init.h"

extern "C" REX_FUNC(sub_82359A78) {
  ctx.r11.u64 = 0x82CE0000u;
  ctx.r10.u64 = REX_LOAD_U32(0x82CD9B08u);
  ctx.cr6.compare<uint32_t>(ctx.r10.u32, 0, ctx.xer);
  if (ctx.cr6.eq) {
    ctx.r3.u64 = 0;
    return;
  }
  ctx.r11.u64 = ctx.r10.u32;
  ctx.ctr.u64 = ctx.r11.u64;
  REX_CALL_INDIRECT_FUNC(ctx.ctr.u32);
}

extern "C" REX_FUNC(sub_824524B4) {
  ctx.r11.u64 = REX_LOAD_U32(ctx.r3.u32 + 8);
  while (ctx.r11.u32 != 0) {
    ctx.r10.u64 = REX_LOAD_U16(ctx.r11.u32 + 0);
    if (ctx.r10.u32 == 3) {
      ctx.cr6.compare<uint32_t>(ctx.r10.u32, 3, ctx.xer);
      ctx.r3.u64 = 0;
      return;
    }
    ctx.r11.u64 = REX_LOAD_U32(ctx.r11.u32 + 8);
  }
  ctx.cr6.compare<uint32_t>(ctx.r11.u32, 0, ctx.xer);
  ctx.r3.u64 = 1;
}

namespace mtg12::hot {
void ConfigureDispatch(bool) {}
}  // namespace mtg12::hot
