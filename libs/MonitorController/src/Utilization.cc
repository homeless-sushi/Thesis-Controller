#include "MonitorController/Utilization.h"

#include <string>
#include <iostream>	

#include <cstdio>	
#include <cstdlib> 
#include <cstring>

#include <unistd.h>

Utilization::Utilization(int numOfCores) {
  this->numOfCores=numOfCores;
  for(int i=0; i<numOfCores; i++){
    prevUserUtilization.push_back(0);
    prevSystemUtilization.push_back(0);
    prevIdleUtilization.push_back(0);
  }
  this->computeUtilization();
}

int Utilization::calUtilization(
    int cpu_idx, 
    long int user, 
    long int nice, 
    long int system, 
    long int idle, 
    long int iowait, 
    long int irq, 
    long int softirq, 
    long int steal) 
{
  long int total = 0;
  int usage = 0;
  long int diff_user, diff_system, diff_idle;
  long int curr_user, curr_system, curr_idle;

  curr_user = (user+nice);
  curr_system = (system+irq+softirq+steal);
  curr_idle = (idle+iowait);

  diff_user = prevUserUtilization[cpu_idx] - curr_user;
  diff_system = prevSystemUtilization[cpu_idx] - curr_system;
  diff_idle = prevIdleUtilization[cpu_idx] - curr_idle;

  total = diff_user + diff_system + diff_idle;
  if (total != 0)
    usage = (diff_user + diff_system) * 100 / total;

  prevUserUtilization[cpu_idx] = curr_user;
  prevSystemUtilization[cpu_idx] = curr_system;
  prevIdleUtilization[cpu_idx] = curr_idle;

  return usage;
}

std::vector<int> Utilization::computeUtilization()
{
  char buf[80] = {'\0',};
  char cpuid[8] = {'\0',};
  long int user, system, nice, idle, iowait, irq, softirq, steal;
  FILE *fp;
  int cpu_index;
  std::vector<int> currUtilizations;
  int error;

  for(int i = 0; i < this->numOfCores; i++)
    currUtilizations.push_back(0);

  fp = fopen("/proc/stat", "r");
  if (fp == NULL)
    return currUtilizations;

  error = 0;
  if(fgets(buf, 80, fp)==NULL) //discard first line since it contains aggregated values for the CPU
    error= 1; 

  cpu_index = 0;
    
  char *r = fgets(buf, 80, fp);
  while (r && cpu_index < numOfCores) {
      char temp[5] = "cpu";
      temp[3] = '0' + cpu_index;
      temp[4] = '\0';
      
      if(!strncmp(buf, temp, 4)){
          sscanf(buf, "%s %ld %ld %ld %ld %ld %ld %ld %ld", cpuid, &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal);
          currUtilizations[cpu_index] = calUtilization(cpu_index, user, nice, system, idle, iowait, irq, softirq, steal);
          r = fgets(buf, 80, fp);
      }
      cpu_index++;
  }
  fclose(fp);

  return currUtilizations;
}
