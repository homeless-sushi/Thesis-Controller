#include "ThesisController/ExamplePolicy.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

#include <csignal>

#include "AppRegisterServer/Policy.h"

#define N_CORES 4
#define CONTROL_PERIOD 1000


void SetupSignals();

bool stop = false;

int main()
{
    SetupSignals();

    std::unique_ptr<Policy::Policy> policy(new Policy::ExamplePolicy(N_CORES));

    unsigned int i = 0;
    while(!stop){
        policy->run(i);

        std::this_thread::sleep_for(std::chrono::milliseconds(CONTROL_PERIOD));

        i++;
    }
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
