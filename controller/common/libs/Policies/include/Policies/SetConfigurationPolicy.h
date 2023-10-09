#ifndef POLICIES_SET_CONFIGURATION_POLICY_H
#define POLICIES_SET_CONFIGURATION_POLICY_H

#include <fstream>
#include <map>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"
#include "AppRegisterServer/Frequency.h"

namespace Policy
{
    class SetConfigurationPolicy : public Policy
    {
        class Config 
        {
            public: 
                struct AppConfig
                {
                    bool gpu;
                    std::vector<int> cores;

                    AppConfig() : 
                        gpu{false},
                        cores{0}
                    {};

                    AppConfig(
                        bool gpu,
                        std::vector<int> cores
                    ) : 
                        gpu{gpu},
                        cores{cores}
                    {};
                };
            
            private:
                Frequency::CPU_FRQ cpuFrq;
                Frequency::GPU_FRQ gpuFrq;

                std::map<std::string, AppConfig> appConfigs;
            
            public:
                Config(
                    Frequency::CPU_FRQ cpuFrq,
                    Frequency::GPU_FRQ gpuFrq,
                    std::map<std::string, AppConfig> appConfigs
                ) :
                    gpuFrq{gpuFrq},
                    cpuFrq{cpuFrq},
                    appConfigs{appConfigs}
                {};
                

                Frequency::CPU_FRQ getCpuFrq() { return cpuFrq; }
                Frequency::GPU_FRQ getGpuFrq() { return gpuFrq; }
                AppConfig& getAppConfig(std::string name) { return appConfigs[name]; }
        };

        private:
            std::set<pid_t> newRegisteredApps; /**< Apps that have been added this cycle */
            std::set<pid_t> runningApps;       /**< Apps that have been running */
            
            std::fstream controllerLogFile;

            Utilization::Utilization utilization;

            Sensors::Sensors sensors;
            std::fstream sensorLogFile;

            Config config;

            Config readConfig(std::string configFileUrl);

        public:
            SetConfigurationPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                std::string sensorsLogUrl,
                std::string configFileUrl
            );

            void run(int cycle) override;
    };
}

#endif //POLICIES_SET_CONFIGURATION_POLICY_H