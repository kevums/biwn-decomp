.text
.macro provider name
.globl \name
\name:
/* The component harness must intercept these declared bus/service entries. */
illegal
rts
.endm
provider native_read8
provider native_read16
provider native_read32
provider native_write16
provider native_write32
provider native_service
