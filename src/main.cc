#include "ThesisController/DummyPolicy.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

#include <csignal>

#include "AppRegisterServer/Policy.h"

#define N_CORES 16
#define CONTROL_PERIOD 1000


bool stop = false;

int main()
{
    // Stop when Ctrl+C is called
    std::signal(SIGINT, [](int signal){
        if (signal == SIGINT) {
            std::cerr << std::endl << "Controller stop" << std::endl;
            stop = true;
        }
    });

    std::unique_ptr<Policy::Policy> policy(new Policy::DummyPolicy(N_CORES));

    unsigned int i = 0;
    while(!stop){
        policy->run(i);

        std::this_thread::sleep_for(std::chrono::milliseconds(CONTROL_PERIOD));

        i++;
    }
}