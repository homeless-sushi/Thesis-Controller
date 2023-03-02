#ifndef MONITOR_CONTROLLER_POLICY
#define MONITOR_CONTROLLER_POLICY

class Policy 
{
    public:
        virtual void run(int cycle) = 0;
        virtual ~Policy() = default;
};

#endif //MONITOR_CONTROLLER_POLICY