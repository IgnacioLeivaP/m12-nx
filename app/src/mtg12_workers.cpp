// Magic 2012 TU #3: idle backoff called from the locally generated worker.
#include <chrono>
#include <thread>
#include <rex/cvar.h>
REXCVAR_DEFINE_INT32(mtg12_worker_idle_us, 100, "Mtg12",
    "Sleep after 64 empty worker polls; 0 restores busy polling").range(0, 5000);
extern "C" void mtg12_worker_idle() {
  static thread_local unsigned polls = 0;
  const int us = REXCVAR_GET(mtg12_worker_idle_us);
  if (us > 0 && ++polls >= 64) {
    polls = 0;
    std::this_thread::sleep_for(std::chrono::microseconds(us));
  }
}
