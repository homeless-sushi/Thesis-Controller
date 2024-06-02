#ifndef FINALPOLICY_FINALPOLICY_H
#define FINALPOLICY_FINALPOLICY_H

#include <fstream>
#include <set>
#include <string>

#include <sys/types.h>

#include "AppRegisterServer/Policy.h"
#include "AppRegisterServer/Sensors.h"
#include "AppRegisterServer/Utilization.h"

#include <zmqpp/zmqpp.hpp>

namespace Policy
{
    class FinalPolicy : public Policy
    {
        private:            
            std::fstream controllerLogFile;
            std::fstream sensorLogFile;

            Utilization::Utilization utilization;
            Sensors::Sensors sensors;

            // ZMQ
            zmqpp::context context;
            zmqpp::socket socket;
            
        public:
            FinalPolicy(
                unsigned nCores,
                std::string controllerLogUrl,
                std::string sensorsLogUrl,
                std::string serverEndpoint);

            ~FinalPolicy() override = default;

            void run(int cycle) override;
    };
}

#endif //FINALPOLICY_FINALPOLICY_H