#include <Utils/Estimation.h>

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
    )
    {
        const float currTime = 1/currThroughput;
        const float utilizationRatio = static_cast<float>(currUtilization)/newUtilization;
        const float frequencyRatio = static_cast<float>(static_cast<unsigned>(currFreq))/static_cast<unsigned>(newFreq);
        const float cpusRatio = static_cast<float>(currCpus)/newCpus;
        const float p = kernelPercent/100;

        return 1/(currTime*utilizationRatio*frequencyRatio*(cpusRatio*p + (1-p)));
    };

    float estimateThroughputGpu(
        float currThroughput,
        unsigned newUtilization,
        unsigned currUtilization,
        Frequency::CPU_FRQ newCpuFreq,
        Frequency::CPU_FRQ currCpuFreq,
        Frequency::GPU_FRQ newGpuFreq,
        Frequency::GPU_FRQ currGpuFreq,
        float kernelPercent
    )
    {
        const float currTime = 1/currThroughput;
        const float utilizationRatio = static_cast<float>(currUtilization)/newUtilization;
        const float cpuFreqRatio = static_cast<float>(static_cast<unsigned>(currCpuFreq))/static_cast<unsigned>(newCpuFreq);
        const float gpuFreqRatio = static_cast<float>(static_cast<unsigned>(currGpuFreq))/static_cast<unsigned>(newGpuFreq);
        const float p = kernelPercent/100;

        return 1/(currTime*utilizationRatio*cpuFreqRatio*(1-p) + currTime*gpuFreqRatio*p);
    };

    struct PowerInfo
    {
        float idle;
        float saturatedCore0;
        float saturatedCore1;
        float saturatedCore2;
        float saturatedCore3;

        PowerInfo(){};

        PowerInfo(
            float idle,
            float saturatedCore0,
            float saturatedCore1,
            float saturatedCore2,
            float saturatedCore3
        ) : 
            idle{idle},
            saturatedCore0{saturatedCore0},
            saturatedCore1{saturatedCore1},
            saturatedCore2{saturatedCore2},
            saturatedCore3{saturatedCore3}
        {};
    };
        

    float estimatePowerCpu(
        float u0Percent,
        float u1Percent,
        float u2Percent,
        float u3Percent,
        Frequency::CPU_FRQ currCpuFreq
    )
    {
        std::map<Frequency::CPU_FRQ, PowerInfo> freqPowerInfo{
            {Frequency::CPU_FRQ::FRQ_102000KHz, {85.0,85.0,128.0,213.842,256.0}},
            {Frequency::CPU_FRQ::FRQ_204000KHz, {85.0,128.0,213.6,341.85,438.95}},
            {Frequency::CPU_FRQ::FRQ_307200KHz, {87.15,171.0,305.3,469.35,596.2}},
            {Frequency::CPU_FRQ::FRQ_403200KHz, {85.0,213.0,404.0,594.0,762.9}},
            {Frequency::CPU_FRQ::FRQ_518400KHz, {85.0,257.15,509.9,721.15,973.9}},
            {Frequency::CPU_FRQ::FRQ_614400KHz, {89.53,297.85,594.0,848.0,1137.75}},
            {Frequency::CPU_FRQ::FRQ_710400KHz, {91.79,348.6,679.0,974.2,1297.1}},
            {Frequency::CPU_FRQ::FRQ_825600KHz, {100.84,425.0,799.15,1123.75,1477.0}},
            {Frequency::CPU_FRQ::FRQ_921600KHz, {112.16,468.0,848.0,1232.45,1641.7}},
            {Frequency::CPU_FRQ::FRQ_1036800KHz, {116.63,509.95,940.85,1393.45,1820.0}},
            {Frequency::CPU_FRQ::FRQ_1132800KHz, {114.31,552.5,1016.0,1480.1,1936.25}},
            {Frequency::CPU_FRQ::FRQ_1224000KHz, {119.2,637.0,1184.3,1729.9,2265.2}},
            {Frequency::CPU_FRQ::FRQ_1326000KHz, {115.0,725.8,1385.8,2018.15,2631.7}},
            {Frequency::CPU_FRQ::FRQ_1428000KHz, {127.78,848.0,1603.05,2306.9,3043.15}},
            {Frequency::CPU_FRQ::FRQ_1479000KHz, {123.6,914.1,1705.9,2477.2,3248.5}}
        };

        const float u0 = u0Percent/100;
        const float u1 = u1Percent/100;
        const float u2 = u2Percent/100;
        const float u3 = u3Percent/100;

        PowerInfo currPowerInfo(freqPowerInfo[currCpuFreq]);

        return ( currPowerInfo.idle 
            + u0 * (currPowerInfo.saturatedCore0 - currPowerInfo.idle)
            + u1 * (currPowerInfo.saturatedCore1 - currPowerInfo.saturatedCore0)
            + u2 * (currPowerInfo.saturatedCore2 - currPowerInfo.saturatedCore1)
            + u3 * (currPowerInfo.saturatedCore3 - currPowerInfo.saturatedCore2)
        );
    };
    
    //estimatePowerGpu(){};
}