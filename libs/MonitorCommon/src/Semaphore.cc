#include "MonitorCommon/Semaphore.h"

#include <fstream>
#include <iostream>

#include <sys/sem.h>

void binarySemaphoreWait(int semId)
{
  struct sembuf operations[1];
  operations[0].sem_num = 0;
  operations[0].sem_op  = -1;
  operations[0].sem_flg = SEM_UNDO;
  int retval = semop (semId, operations, 1);
  if (retval == -1){
    std::cout << "Something wrong happened during sempahore wait" << std::endl;
    exit(EXIT_FAILURE); 
  }
}

void binarySemaphorePost(int semId) 
{
  struct sembuf operations[1];
  operations[0].sem_num = 0;
  operations[0].sem_op  = 1;
  operations[0].sem_flg = SEM_UNDO;
  int retval = semop (semId, operations, 1);
  if (retval == -1){
    std::cout << "Something wrong happened during sempahore post" << std::endl;
    exit(EXIT_FAILURE); 
  }
}

