#include "Policies/GpuPowerModelPolicy.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

#include <csignal>

#include "AppRegisterServer/Policy.h"

#include <boost/program_options.hpp>

#define N_CORES 4
#define CONTROL_PERIOD 1000
#define N_SAMPLES 10

namespace po = boost::program_options;
po::options_description SetupOptions();

void SetupSignals();

bool stop = false;

int main(int argc, char *argv[])
{
    SetupSignals();

    po::options_description desc(SetupOptions());
    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    if (vm.count("help"))
    {
        std::cout << desc << "\n";
        return 0;
    }

    std::string controllerLogUrl(vm["controller-log"].as<std::string>());
    std::string sensorsLogUrl(vm["sensors-log"].as<std::string>());
    std::unique_ptr<Policy::Policy> policy(
        new Policy::GpuPowerModelPolicy(
            N_CORES,
            controllerLogUrl,
            20,
            sensorsLogUrl
    ));

    unsigned int i = 0;
    while(!stop){

        for(unsigned j = 0; j < N_SAMPLES-1; ++j){
            Policy::GpuPowerModelPolicy* ptr(dynamic_cast<Policy::GpuPowerModelPolicy*>(policy.get()));
            ptr->sense();
            std::this_thread::sleep_for(std::chrono::milliseconds(CONTROL_PERIOD/N_SAMPLES));
        }

        policy->run(i);
        std::this_thread::sleep_for(std::chrono::milliseconds(CONTROL_PERIOD/N_SAMPLES));

        i++;
    }
}

po::options_description SetupOptions()
{
    po::options_description desc("Allowed options");
    desc.add_options()
    ("help", "Display help message")
    ("controller-log,L", po::value<std::string>(), "the URL to output the controller log to")
    ("sensors-log", po::value<std::string>(), "the URL to output the sensors log to")
    ;

    return desc;
}

void SetupSignals()
{
    auto stopController = [](int signal){
        std::cerr << std::endl;
        std::cerr << "Received signal: " << signal << std::endl;
        std::cerr << "Stopping controller" << std::endl;

        stop = true;
    };

    std::signal(SIGINT, stopController);
    std::signal(SIGTERM, stopController);

}
