#ifndef MONITOR_CONTROLLER_MONITOR_POLICY
#define MONITOR_CONTROLLER_MONITOR_POLICY

#include "MonitorController/Policy.h"
#include "MonitorController/Utilization.h"
#include "MonitorCommon/Monitor.h"

class MonitorPolicy: public Policy
{
    public:
        MonitorPolicy(bool sensorsEnabled = false);
        ~MonitorPolicy();
        void run(int cycle);

    private:
        bool sensorsEnabled;
        monitor_t* appl_monitor;
        Utilization* utilization;
};

#endif //MONITOR_CONTROLLER_MONITOR_POLICY