#ifndef UTILS_ESTIMATION_H
#define UTILS_ESTIMATION_H

#include <map>

#include "AppRegisterServer/Frequency.h"

namespace Estimation
{
    float estimateThroughputCpu(
        float currThroughput,
        unsigned newUtilization,
        unsigned currUtilization,
        Frequency::CPU_FRQ newFreq,
        Frequency::CPU_FRQ currFreq,
        unsigned newCpus,
        unsigned currCpus,
        float kernelPercent
    );

    float estimateThroughputGpu(
        float currThroughput,
        unsigned newUtilization,
        unsigned currUtilization,
        Frequency::CPU_FRQ newCpuFreq,
        Frequency::CPU_FRQ currCpuFreq,
        Frequency::GPU_FRQ newGpuFreq,
        Frequency::GPU_FRQ currGpuFreq,
        float kernelPercent
    );        

    float estimatePowerCpu(
        float u0Percent,
        float u1Percent,
        float u2Percent,
        float u3Percent,
        Frequency::CPU_FRQ currCpuFreq
    );

    //estimatePowerGpu(){};
}

#endif //UTILS_ESTIMATION_H