/* Read-only execution counters. Algorithm/helper/CPU equivalence is a separate
 * finite component proof. The qualified movement monitor checks its full nested
 * stack and movement-context canary while real collision/geometry code runs. */
static uint64_t ac_entries[2],ac_native[2],ac_returns[2],ac_original_steps,ac_native_steps;
static uint64_t ac_pending,ac_counter_errors;
static void watch_actor_collision(uint32_t pc){
 if(pc==0x13b5au){ac_entries[0]++;ac_pending++;}
 if(pc==0x13bb0u){ac_entries[1]++;ac_pending++;}
 if(pc==__AC_OUTDOOR_ENTRY__)ac_native[0]++;
 if(pc==__AC_INDOOR_ENTRY__)ac_native[1]++;
 if((pc>0x13b5au&&pc<0x13bb0u)||(pc>0x13bb0u&&pc<0x13c9au))ac_original_steps++;
 if(pc>=__AC_START__&&pc<__AC_END__)ac_native_steps++;
 if(pc==__AC_OUTDOOR_RETURN__||pc==0x13baeu){ac_returns[0]++;if(ac_pending)ac_pending--;else ac_counter_errors++;}
 if(pc==__AC_INDOOR_RETURN__||pc==0x13c98u){ac_returns[1]++;if(ac_pending)ac_pending--;else ac_counter_errors++;}
}
